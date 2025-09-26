import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Any, Literal

import numpy as np

from ..cache.builder import build_cache
from ..cache.local_cache import LocalCache
from ..data_structures.motion_clip import MotionClip
from ..data_structures.restpose import Restpose
from ..io.file.builder import build_file_reader
from ..io.meta.builder import build_meta_reader
from ..io.motion.builder import build_motion_reader
from ..utils.super import Super

if TYPE_CHECKING:
    from ..io.file.base_file_reader import BaseFileReader
    from ..io.meta.base_meta_reader import BaseMetaReader
    from ..io.motion.base_motion_reader import BaseMotionReader


class MotionFileApiV1(Super):
    """V1 version motion files downloader.

    This class provides a high-level API for accessing motion data, mesh data,
    and restpose data with caching capabilities. It supports automatic cache
    maintenance and version checking to ensure data consistency.
    """

    def __init__(
            self,
            meta_reader_cfg: dict[str, Any],
            motion_reader_cfg: dict[str, Any],
            restpose_reader_cfg: dict[str, Any],
            mesh_reader_cfg: dict[str, Any],
            joints_meta_reader_cfg: dict[str, Any],
            rigids_meta_reader_cfg: dict[str, Any],
            blendshapes_meta_reader_cfg: dict[str, Any],
            cache_cfg: dict[str, Any],
            maintain_check_interval: int = 60,
            max_workers: int = 4,
            thread_pool_executor: ThreadPoolExecutor | None = None,
            logger_cfg: None | dict[str, Any] = None):
        """Initialize the motion file API.

        Args:
            meta_reader_cfg (dict[str, Any]):
                Configuration for meta data reader.
            motion_reader_cfg (dict[str, Any]):
                Configuration for motion data reader.
            restpose_reader_cfg (dict[str, Any]):
                Configuration for restpose data reader.
            mesh_reader_cfg (dict[str, Any]):
                Configuration for mesh data reader.
            cache_cfg (dict[str, Any]):
                Configuration for cache system.
            maintain_check_interval (int, optional):
                Interval in seconds for cache maintenance checks. Defaults to 60.
            max_workers (int, optional):
                Maximum number of worker threads. Defaults to 4.
            thread_pool_executor (ThreadPoolExecutor | None, optional):
                Thread pool executor.
                If None, a new thread pool executor will be created
                based on max_workers. Defaults to None.
                If None, a new executor will be created. Defaults to None.
            logger_cfg (None | dict[str, Any], optional):
                Logger configuration, see `setup_logger` for detailed description.
                Logger name will use the class name. Defaults to None.
        """
        super().__init__(logger_cfg)
        self.meta_reader_cfg = meta_reader_cfg
        self.motion_reader_cfg = motion_reader_cfg
        self.restpose_reader_cfg = restpose_reader_cfg
        self.mesh_reader_cfg = mesh_reader_cfg
        self.joints_meta_reader_cfg = joints_meta_reader_cfg
        self.rigids_meta_reader_cfg = rigids_meta_reader_cfg
        self.blendshapes_meta_reader_cfg = blendshapes_meta_reader_cfg
        self.cache_cfg = cache_cfg

        self.max_workers = max_workers
        if thread_pool_executor is None:
            self.thread_pool_executor = ThreadPoolExecutor(
                max_workers=max_workers)
        else:
            self.thread_pool_executor = thread_pool_executor
        self.executor_external = True \
            if thread_pool_executor is not None \
            else False

        # Cache layer and IO instances that cache updates depend on
        self.meta_reader: BaseMetaReader | None = None
        self.motion_reader: BaseMotionReader | None = None
        self.restpose_reader: BaseFileReader | None = None
        self.mesh_reader: BaseFileReader | None = None
        self.joints_meta_reader: BaseFileReader | None = None
        self.rigids_meta_reader: BaseFileReader | None = None
        self.blendshapes_meta_reader: BaseFileReader | None = None
        self.maintain_check_interval = maintain_check_interval
        self.cache: LocalCache | None = None
        self.next_cache_instance: LocalCache | None = None
        self.next_cache_task: asyncio.Task | None = None
        self.last_maintain_check_time: float = 0

        self.startup_called: bool = False

        # Log file path
        log_path = None
        for logger_handler in self.logger.handlers:
            if hasattr(logger_handler, "baseFilename"):
                log_path = logger_handler.baseFilename
                break
        self.log_path = log_path

    def __del__(self) -> None:
        """Destructor for cleanup of thread pool executor.

        This method ensures proper cleanup of the thread pool executor
        if it was created internally by this instance.
        """
        if not self.executor_external:
            self.thread_pool_executor.shutdown(wait=True)


    async def startup(self) -> None:
        """Start up the motion file API.

        This method initializes all required readers, builds the cache system,
        and performs initial cache synchronization. It should be called once
        before using any other API methods.

        Raises:
            RuntimeError:
                If the API has already been started.
        """
        if self.startup_called:
            msg = 'API has already been started, please do not start again.'
            self.logger.error(msg)
            raise RuntimeError(msg)
        self._build_readers()
        local_cache = self._build_cache()
        self.logger.info(
            'Performing initial cache sync during startup...'
        )
        await local_cache.sync()
        self.cache = local_cache
        self.logger.info('Startup completed.')
        self.startup_called = True

    async def get_mesh(self, name: str) -> bytes:
        """Get mesh data for a specific avatar.

        This method retrieves 3D mesh data for the specified avatar name
        from the cache system.

        Args:
            name (str):
                Name of the avatar to get mesh data for.

        Returns:
            bytes:
                Binary mesh data in the configured format.
        """
        await self._maintain_check()
        return await self.cache.get_mesh_by_name(name)

    async def get_joints_meta(self, name: str) -> bytes:
        """Get joints metadata for a specific avatar.

        This method retrieves joint hierarchy and configuration metadata
        for the specified avatar name from the cache system.

        Args:
            name (str):
                Name of the avatar to get joints metadata for.

        Returns:
            bytes:
                Binary joints metadata in the configured format.
        """
        await self._maintain_check()
        return await self.cache.get_joints_meta_by_name(name)

    async def get_rigids_meta(self, name: str) -> bytes:
        """Get rigids metadata for a specific avatar.

        This method retrieves rigid body physics metadata for the specified
        avatar name from the cache system.

        Args:
            name (str):
                Name of the avatar to get rigids metadata for.

        Returns:
            bytes:
                Binary rigids metadata in the configured format.
        """
        await self._maintain_check()
        return await self.cache.get_rigids_meta_by_name(name)

    async def get_blendshapes_meta(self, name: str) -> bytes:
        """Get blendshapes metadata for a specific avatar.

        This method retrieves facial blendshape configuration metadata
        for the specified avatar name from the cache system.

        Args:
            name (str):
                Name of the avatar to get blendshapes metadata for.

        Returns:
            bytes:
                Binary blendshapes metadata in the configured format.
        """
        await self._maintain_check()
        return await self.cache.get_blendshapes_meta_by_name(name)

    async def get_motion_keywords(self) -> set[str]:
        """Get motion keywords.

        Returns:
            set[str]: Set of motion keywords.
        """
        await self._maintain_check()
        return await self.cache.get_motion_keywords()

    async def get_restpose(self, name: str) -> Restpose:
        """Get restpose data for a specific avatar.

        This method retrieves the static pose (T-pose or A-pose) data
        for the specified avatar name from the cache system.

        Args:
            name (str):
                Name of the avatar to get restpose data for.

        Returns:
            Restpose:
                Static pose data containing joint hierarchy, local matrices,
                and world transformation matrices.
        """
        await self._maintain_check()
        return await self.cache.get_restpose_by_name(name)

    async def get_motion(
            self,
            name: str,
            app_name: Literal['python_backend', 'babylon'] = 'python_backend'
            ) -> list[tuple[dict[str, Any], MotionClip]]:
        """Get all motion clips available for the specified avatar.

        This method retrieves all motion clips associated with the specified
        avatar and optionally converts them to the target application format.
        Each motion clip includes metadata and animation data.

        Args:
            name (str):
                Name of the avatar to get motion data for.
            app_name (Literal['python_backend', 'babylon'], optional):
                Target application format for motion data conversion.
                Defaults to 'python_backend'.

        Returns:
            list[tuple[dict[str, Any], MotionClip]]:
                List of tuples containing motion metadata dictionaries and
                corresponding motion clip objects available for the avatar.
        """
        await self._maintain_check()
        motion_record_ids = await self.cache.get_motion_record_ids_by_avatar(name)
        return_list = []
        meta_dicts = []
        motion_clips = []
        coroutines = []
        for motion_record_id in motion_record_ids:
            meta_dict = await self.cache.get_meta_by_id(motion_record_id)
            meta_dicts.append(meta_dict)
            coroutine = self.cache.get_motion_clip_by_id(motion_record_id)
            coroutines.append(coroutine)
        motion_clips = await asyncio.gather(*coroutines)
        coroutines = []
        if app_name != 'python_backend':
            for motion_clip in motion_clips:
                coroutine = self._convert_motion_clip_app(motion_clip, app_name)
                coroutines.append(coroutine)
            motion_clips = await asyncio.gather(*coroutines)
        else:
            motion_clips = motion_clips
        for meta_dict, motion_clip in zip(meta_dicts, motion_clips, strict=True):
            return_list.append((meta_dict, motion_clip))
        return return_list

    async def _maintain_check(self) -> None:
        """Check if cache needs updating and handle expired requests.

        This method performs periodic maintenance checks to ensure cache
        consistency and handles background cache updates.
        """
        # Check cache
        if self.next_cache_instance is not None:
            if self.next_cache_task.done():
                msg = 'Cache update task completed, replacing cache...'
                self.logger.info(msg)
                self.cache = self.next_cache_instance
                self.next_cache_instance = None
                self.next_cache_task = None
                msg = 'Cache replacement completed'
                self.logger.info(msg)
                return
        cur_time = time.time()
        if cur_time - self.last_maintain_check_time > self.maintain_check_interval:
            self.last_maintain_check_time = cur_time
            # Check if cache version matches meta_reader version
            cache_version = await self.cache.get_version()
            meta_version = await self.meta_reader.get_version()
            # Start cache update task in background
            if cache_version != meta_version:
                msg = f'Found cache layer version {cache_version}' +\
                    f' inconsistent with IO layer version {meta_version}' +\
                    ', starting cache update task...'
                self.logger.info(msg)
                self.next_cache_instance = self._build_cache()
                self.next_cache_task = asyncio.create_task(
                    self.next_cache_instance.sync())

    def _build_readers(self) -> None:
        """Build all required reader instances.

        This method initializes all required reader instances (meta, motion,
        restpose, mesh, and metadata readers) using their respective
        configuration dictionaries and logger settings.

        The readers are built with proper logger configuration and thread
        pool executor where applicable.
        """
        meta_reader_cfg = self.meta_reader_cfg.copy()
        meta_reader_cfg['logger_cfg'] = self.logger_cfg
        self.meta_reader = build_meta_reader(meta_reader_cfg)
        motion_reader_cfg = self.motion_reader_cfg.copy()
        motion_reader_cfg['logger_cfg'] = self.logger_cfg
        motion_reader_cfg['thread_pool_executor'] = self.thread_pool_executor
        self.motion_reader = build_motion_reader(motion_reader_cfg)
        restpose_reader_cfg = self.restpose_reader_cfg.copy()
        restpose_reader_cfg['logger_cfg'] = self.logger_cfg
        self.restpose_reader = build_file_reader(restpose_reader_cfg)
        mesh_reader_cfg = self.mesh_reader_cfg.copy()
        mesh_reader_cfg['logger_cfg'] = self.logger_cfg
        self.mesh_reader = build_file_reader(mesh_reader_cfg)
        joints_meta_reader_cfg = self.joints_meta_reader_cfg.copy()
        joints_meta_reader_cfg['logger_cfg'] = self.logger_cfg
        self.joints_meta_reader = build_file_reader(joints_meta_reader_cfg)
        rigids_meta_reader_cfg = self.rigids_meta_reader_cfg.copy()
        rigids_meta_reader_cfg['logger_cfg'] = self.logger_cfg
        self.rigids_meta_reader = build_file_reader(rigids_meta_reader_cfg)
        blendshapes_meta_reader_cfg = self.blendshapes_meta_reader_cfg.copy()
        blendshapes_meta_reader_cfg['logger_cfg'] = self.logger_cfg
        self.blendshapes_meta_reader = build_file_reader(blendshapes_meta_reader_cfg)

    def _build_cache(self) -> LocalCache:
        """Build cache instance with all required readers.

        This method creates a new cache instance configured with all
        the required readers and their configurations.

        Returns:
            LocalCache:
                Configured cache instance with all readers attached.
        """
        cache_cfg = self.cache_cfg.copy()
        cache_cfg['logger_cfg'] = self.logger_cfg
        cache_cfg['thread_pool_executor'] = self.thread_pool_executor
        cache_cfg['meta_reader'] = self.meta_reader
        cache_cfg['motion_reader'] = self.motion_reader
        cache_cfg['restpose_reader'] = self.restpose_reader
        cache_cfg['mesh_reader'] = self.mesh_reader
        cache_cfg['joints_meta_reader'] = self.joints_meta_reader
        cache_cfg['rigids_meta_reader'] = self.rigids_meta_reader
        cache_cfg['blendshapes_meta_reader'] = self.blendshapes_meta_reader
        for key in list(cache_cfg.keys()):
            if key.endswith('_cfg_template'):
                cache_cfg[key]['logger_cfg'] = self.logger_cfg
        return build_cache(cache_cfg)


    async def _convert_motion_clip_app(
            self,
            src_motion_clip: MotionClip,
            dst_app_name: Literal['babylon']
            ) -> MotionClip:
        """Convert motion clip to target application format.

        This method converts a motion clip from the internal library format
        to the specified target application format (currently supports Babylon.js).

        Args:
            src_motion_clip (MotionClip):
                Source motion clip in library format (app_name as None).
            dst_app_name (Literal['babylon']):
                Target application format for conversion.

        Returns:
            MotionClip:
                Converted motion clip with app_name set to target format.

        Raises:
            ValueError:
                If the specified app_name is not supported.
        """
        restpose_name = src_motion_clip.restpose_name
        restpose = await self.cache.get_restpose_by_name(restpose_name)
        loop = asyncio.get_running_loop()
        if dst_app_name == 'babylon':
            dst_joint_names, dst_rotmat, dst_root_world_position = \
                await loop.run_in_executor(
                    self.thread_pool_executor,
                    self._convert_to_babylon,
                    restpose,
                    src_motion_clip.joint_names,
                    src_motion_clip.joint_rotmat,
                    src_motion_clip.root_world_position
                )
            ret_motion_clip = src_motion_clip.clone()
            ret_motion_clip.app_name = 'babylon'
            ret_motion_clip.set_joint_rotmat(
                joint_rotmat=dst_rotmat,
                joint_names=dst_joint_names
            )
            ret_motion_clip.set_root_world_position(
                root_world_position=dst_root_world_position
            )
            return ret_motion_clip
        else:
            msg = f'Unsupported app_name: {dst_app_name}'
            self.logger.error(msg)
            raise ValueError(msg)

    def _convert_to_babylon(
            self,
            restpose: Restpose,
            src_joint_names: list[str],
            src_matrix_basis: np.ndarray,
            src_root_world_position: np.ndarray,
            ) -> tuple[list[str], np.ndarray, np.ndarray]:
        """Convert motion data to Babylon.js application format.

        This method performs coordinate system transformations and matrix
        conversions to make motion data compatible with Babylon.js rendering
        engine, including coordinate system changes and parent space transforms.

        Args:
            restpose (Restpose):
                Static pose data containing joint hierarchy and local matrices.
            src_joint_names (list[str]):
                Source joint names from the motion data.
            src_matrix_basis (np.ndarray):
                Source rotation matrices in world coordinate system with shape
                (n_frames, n_joints, 3, 3), where n_joints=len(src_joint_names).
            src_root_world_position (np.ndarray):
                Root bone position in source world coordinate system.

        Returns:
            tuple[list[str], np.ndarray, np.ndarray]:
                list[str]: Converted joint names list, which can be different
                    from src_joint_names, but should not introduce too many
                    unnecessary bones.
                np.ndarray: Rotation matrices ready for Babylon.js use with
                    shape (n_frames, n_joints, 3, 3).
                np.ndarray: Root bone position in Babylon.js world coordinate
                    system ready for application use.
        """
        n_frames = src_matrix_basis.shape[0]
        n_joints = src_matrix_basis.shape[1]

        # Convert 3x3 rotation matrices to 4x4 motion basis matrices
        eye_4 = np.eye(4, dtype=src_matrix_basis.dtype)
        basis_matrices = np.tile(eye_4, (n_frames, n_joints, 1, 1))
        basis_matrices[:, :, :3, :3] = src_matrix_basis
        # Extract local_matrices corresponding to src_joint_names from
        # Restpose full data
        joint_indices = [
            restpose.get_joint_index(joint_name) for joint_name in src_joint_names]
        joint_indices = np.array(joint_indices, dtype=np.int32)
        local_matrices = restpose.local_matrices[joint_indices]
        # Create a 4D array to store results
        parent_space_transforms = np.zeros((n_frames, n_joints, 4, 4),
                                           dtype=src_matrix_basis.dtype)
        # Temporarily set indices without parent joints to 0 for batch
        # creation of parent_local_mats
        parent_indices = [
            restpose.parent_indices[joint_idx] for joint_idx in joint_indices]
        parent_indices = np.array(parent_indices, dtype=np.int32)
        without_parent_indices = np.where(parent_indices < 0)[0]
        parent_indices[without_parent_indices] = 0
        parent_local_matrices = restpose.local_matrices[parent_indices]
        # Set positions without parent joints to identity matrix to
        # eliminate parent_inv influence
        parent_local_matrices[without_parent_indices] = np.eye(
            4, dtype=src_matrix_basis.dtype)
        parent_inv = np.linalg.inv(parent_local_matrices)
        parent_space_transforms = parent_inv @ local_matrices @ basis_matrices
        # Extract rotation matrices
        tgt_matrices = parent_space_transforms[:, :, :3, :3]
        tgt_transl = src_root_world_position * 100
        tgt_transl[:, [1, 2]] = tgt_transl[:, [2, 1]]
        tgt_transl[:, 2] = -tgt_transl[:, 2]
        return src_joint_names, tgt_matrices, tgt_transl
