import asyncio
import io
import os
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

from ..data_structures.motion_clip import MotionClip
from ..data_structures.restpose import Restpose
from ..io.file.base_file_reader import BaseFileReader
from ..io.meta.base_meta_reader import BaseMetaReader
from ..io.motion.base_motion_reader import BaseMotionReader
from ..utils.log import setup_logger
from ..utils.super import Super


class VersionMismatchError(Exception):
    """Version mismatch error.

    Raised when meta version and motion version do not match.
    """
    pass

class CacheNotReadyError(Exception):
    """Cache not ready error.

    Raised when cache operations are attempted before cache is ready.
    """
    pass

class LocalCache(Super):
    """Local cache using memory and temporary files.

    This class provides caching functionality for motion data, restpose data,
    and mesh data using local memory and temporary file storage.
    """

    def __init__(
            self,
            meta_reader: BaseMetaReader,
            motion_reader: BaseMotionReader,
            max_workers: int = 1,
            thread_pool_executor: ThreadPoolExecutor | None = None,
            restpose_reader: BaseFileReader | None = None,
            mesh_reader: BaseFileReader | None = None,
            joints_meta_reader: BaseFileReader | None = None,
            rigids_meta_reader: BaseFileReader | None = None,
            blendshapes_meta_reader: BaseFileReader | None = None,
            logger_cfg: None | dict = None) -> None:
        """Initialize the local cache.

        Args:
            meta_reader (BaseMetaReader):
                Meta reader instance.
            motion_reader (BaseMotionReader):
                Motion reader instance.
            max_workers (int, optional):
                Maximum number of worker threads. Defaults to 1.
            thread_pool_executor (ThreadPoolExecutor | None, optional):
                Thread pool executor.
                If None, a new thread pool executor will be created based on
                max_workers. Defaults to None.
            restpose_reader (BaseFileReader | None, optional):
                Restpose reader instance. If None, restpose will not be cached.
                Defaults to None.
            mesh_reader (BaseFileReader | None, optional):
                Mesh reader instance. If None, mesh will not be cached.
                Defaults to None.
            joints_meta_reader (BaseFileReader | None, optional):
                Joints meta reader instance. If None, joints meta will not be cached.
                Defaults to None.
            rigids_meta_reader (BaseFileReader | None, optional):
                Rigids meta reader instance. If None, rigids meta will not be cached.
                Defaults to None.
            blendshapes_meta_reader (BaseFileReader | None, optional):
                Blendshapes meta reader instance. If None, blendshapes meta will not be
                cached. Defaults to None.
            logger_cfg (None | dict, optional):
                Logger configuration, see `setup_logger` for detailed description.
                Logger name will use the class name. Defaults to None.
        """
        Super.__init__(self, logger_cfg)
        self.meta_reader = meta_reader
        self.motion_reader = motion_reader
        self.restpose_reader = restpose_reader
        self.mesh_reader = mesh_reader
        self.joints_meta_reader = joints_meta_reader
        self.rigids_meta_reader = rigids_meta_reader
        self.blendshapes_meta_reader = blendshapes_meta_reader
        self.max_workers = max_workers
        self.executor = thread_pool_executor \
            if thread_pool_executor is not None \
            else ThreadPoolExecutor(max_workers=max_workers)
        self.executor_external = True \
            if thread_pool_executor is not None \
            else False

        self.cache_ready = False
        self.version: str | None = None

        self.avatar_mapping: dict[str, set[int]] | None = None
        self.motion_keywords: set[str] | None = None

        self.motion_records: dict[int, dict] | None = None
        self.motion_clips_dir = tempfile.TemporaryDirectory(
            prefix='motion_file_local_cache_')
        self.motion_clips_paths: dict[int, str] | None = None
        self.motion_clips_cache: dict[int, MotionClip] | None = None
        self.restpose_files_dir = tempfile.TemporaryDirectory(
            prefix='motion_file_local_cache_')
        self.restpose_files_paths: dict[str, str] | None = None
        self.restpose_files_cache: dict[str, Restpose] | None = None
        self.mesh_files_dir = tempfile.TemporaryDirectory(
            prefix='motion_file_local_cache_')
        self.mesh_files_paths: dict[str, str] | None = None
        self.joints_files_dir = tempfile.TemporaryDirectory(
            prefix='motion_file_local_cache_')
        self.joints_files_paths: dict[str, str] | None = None
        self.rigids_files_dir = tempfile.TemporaryDirectory(
            prefix='motion_file_local_cache_')
        self.rigids_files_paths: dict[str, str] | None = None
        self.blendshapes_files_dir = tempfile.TemporaryDirectory(
            prefix='motion_file_local_cache_')
        self.blendshapes_files_paths: dict[str, str] | None = None


    def __del__(self) -> None:
        """Destructor."""
        try:
            self.motion_clips_dir.cleanup()
        except Exception as e:
            self.logger.error(f'Failed to cleanup motion_clips_dir: {e}')
        try:
            self.restpose_files_dir.cleanup()
        except Exception as e:
            self.logger.error(f'Failed to cleanup restpose_files_dir: {e}')
        try:
            self.mesh_files_dir.cleanup()
        except Exception as e:
            self.logger.error(f'Failed to cleanup mesh_files_dir: {e}')
        try:
            self.joints_files_dir.cleanup()
        except Exception as e:
            self.logger.error(f'Failed to cleanup joints_files_dir: {e}')
        try:
            self.rigids_files_dir.cleanup()
        except Exception as e:
            self.logger.error(f'Failed to cleanup rigids_files_dir: {e}')
        try:
            self.blendshapes_files_dir.cleanup()
        except Exception as e:
            self.logger.error(f'Failed to cleanup blendshapes_files_dir: {e}')
        if not self.executor_external:
            self.thread_pool_executor.shutdown(wait=True)

    async def get_version(self) -> str:
        """Get cache version.

        Returns:
            str: Cache version string.
        """
        return self.version

    async def sync(self) -> None:
        """Update current cache instance based on IO layer data.

        Raises:
            VersionMismatchError: If meta version and motion version do not match.
        """
        start_time = time.time()
        meta_version = await self.meta_reader.get_version()
        motion_version = await self.motion_reader.get_version()
        # 忽略restpose版本对比, 因为restpose reader版本是常量
        if meta_version != motion_version:
            msg = f'Version mismatch, meta_version: {meta_version}, ' +\
                f'motion_version: {motion_version}'
            self.logger.error(msg)
            raise VersionMismatchError(msg)
        self.logger_cfg['logger_name'] = f'{self.__class__.__name__}-{meta_version}'
        self.logger = setup_logger(**self.logger_cfg)
        # 同步meta数据
        await self._sync_from_meta_reader()
        # 同步motion数据, 需要避免与meta同步并行
        await self._sync_from_motion_reader()
        # 同步restpose数据
        if self.restpose_reader is not None:
            await self._sync_from_restpose_reader()
        else:
            msg = 'restpose_reader not configured during construction, ' +\
                'no restpose caching provided.'
            self.logger.warning(msg)
        # 同步mesh数据
        coroutines = []
        if self.mesh_reader is not None:
            coroutines.append(self._sync_from_mesh_reader())
        else:
            msg = 'mesh_reader not configured during construction, ' +\
                'no mesh caching provided.'
            self.logger.warning(msg)
        if self.joints_meta_reader is not None:
            coroutines.append(self._sync_from_joints_meta_reader())
        else:
            msg = 'joints_meta_reader not configured during construction, ' +\
                'no joints caching provided.'
            self.logger.warning(msg)
        if self.rigids_meta_reader is not None:
            coroutines.append(self._sync_from_rigids_meta_reader())
        else:
            msg = 'rigids_meta_reader not configured during construction, ' +\
                'no rigids caching provided.'
            self.logger.warning(msg)
        if self.blendshapes_meta_reader is not None:
            coroutines.append(self._sync_from_blendshapes_meta_reader())
        else:
            msg = 'blendshapes_meta_reader not configured during construction, ' +\
                'no blendshapes caching provided.'
            self.logger.warning(msg)
        await asyncio.gather(*coroutines)
        # 设置motion_clips_cache
        await self._setup_motion_clips_cache()
        # 设置restpose_cache
        self.restpose_cache = dict()
        # set attrs
        self.version = meta_version
        self.cache_ready = True
        self.logger.info('Local cache preparation completed, ' +\
            f'time taken: {time.time() - start_time:.2f}s')

    async def get_motion_record_ids_by_avatar(self, avatar_name: str) -> list[int]:
        """Get motion record IDs by avatar name.

        Args:
            avatar_name (str): Name of the avatar.

        Returns:
            list[int]: List of motion record IDs.

        Raises:
            CacheNotReadyError: If cache is not ready.
            KeyError: If avatar name is not found.
        """
        if not self.cache_ready:
            msg = 'Cache not ready, unable to get motion_record_ids.'
            self.logger.error(msg)
            raise CacheNotReadyError(msg)
        if avatar_name not in self.avatar_mapping:
            msg = f'No motion_record found for avatar_name={avatar_name}.'
            self.logger.error(msg)
            raise KeyError(msg)
        return list(self.avatar_mapping[avatar_name])

    async def get_meta_by_id(self, motion_record_id: int) -> dict:
        """Get meta data by motion record ID.

        Args:
            motion_record_id (int): Motion record ID.

        Returns:
            dict: Meta data dictionary.

        Raises:
            CacheNotReadyError: If cache is not ready.
        """
        if not self.cache_ready:
            msg = 'Cache not ready, unable to get meta.'
            self.logger.error(msg)
            raise CacheNotReadyError(msg)
        return self.motion_records[motion_record_id]

    async def get_motion_clip_by_id(
            self,
            motion_record_id: int,
            ) -> MotionClip:
        """Get motion clip by motion record ID.

        Args:
            motion_record_id (int): Motion record ID.

        Returns:
            MotionClip: Motion clip data.

        Raises:
            CacheNotReadyError: If cache is not ready.
            KeyError: If motion record ID is not found.
        """
        # TODO: 根据调用数据将部分动作加入motion_clips_cache以提高命中率
        if not self.cache_ready:
            msg = 'Cache not ready, unable to get motion_clip.'
            self.logger.error(msg)
            raise CacheNotReadyError(msg)
        if motion_record_id in self.motion_clips_cache:
            return self.motion_clips_cache[motion_record_id]
        if motion_record_id in self.motion_clips_paths:
            npz_path = self.motion_clips_paths[motion_record_id]
            loop = asyncio.get_running_loop()
            motion_clip = await loop.run_in_executor(
                self.executor,
                _load_motion_clip, npz_path)
            return motion_clip
        msg = f'No motion data record found for ID={motion_record_id}.'
        self.logger.error(msg)
        raise KeyError(msg)

    async def get_restpose_by_name(self, restpose_name: str) -> Restpose:
        """Get restpose by name.

        Args:
            restpose_name (str): Name of the restpose.

        Returns:
            Restpose: Restpose data.

        Raises:
            CacheNotReadyError: If cache is not ready or restpose reader is not
                configured.
            KeyError: If restpose name is not found.
        """
        if not self.cache_ready:
            msg = 'Cache not ready, unable to get restpose.'
            self.logger.error(msg)
            raise CacheNotReadyError(msg)
        if self.restpose_reader is None:
            msg = 'restpose_reader not configured during construction, ' +\
                'unable to get restpose.'
            self.logger.error(msg)
            raise CacheNotReadyError(msg)
        if restpose_name in self.restpose_cache:
            return self.restpose_cache[restpose_name]
        if restpose_name in self.restpose_paths:
            npz_path = self.restpose_paths[restpose_name]
            loop = asyncio.get_running_loop()
            restpose = await loop.run_in_executor(
                self.executor,
                _load_restpose,
                npz_path,
                restpose_name)
            # 因为Restpose总数很少且每个Restpose数据量很小, 所以直接缓存
            self.restpose_cache[restpose_name] = restpose
            return restpose
        msg = f'No restpose data record found for name={restpose_name}.'
        self.logger.error(msg)
        raise KeyError(msg)

    async def get_mesh_by_name(self, mesh_name: str) -> bytes:
        """Get mesh by name.

        Args:
            mesh_name (str): Name of the mesh.

        Returns:
            bytes: Mesh data.

        Raises:
            CacheNotReadyError: If cache is not ready or mesh reader is not configured.
            KeyError: If mesh name is not found.
        """
        if not self.cache_ready:
            msg = 'Cache not ready, unable to get mesh.'
            self.logger.error(msg)
            raise CacheNotReadyError(msg)
        if self.mesh_reader is None:
            msg = 'mesh_reader not configured during construction, ' +\
                'unable to get mesh.'
            self.logger.error(msg)
            raise CacheNotReadyError(msg)
        if mesh_name in self.mesh_files_paths:
            mesh_path = self.mesh_files_paths[mesh_name]
            with open(mesh_path, 'rb') as f:
                mesh_bytes = f.read()
            return mesh_bytes
        msg = f'No mesh data record found for name={mesh_name}.'
        self.logger.error(msg)
        raise KeyError(msg)

    async def get_joints_meta_by_name(self, joints_name: str) -> bytes:
        """Get joints meta by name.

        Args:
            joints_name (str): Name of the joints.

        Returns:
            bytes: Joints meta data.

        Raises:
            CacheNotReadyError: If cache is not ready or joints meta reader is not
                configured.
            KeyError: If joints name is not found.
        """
        if not self.cache_ready:
            msg = 'Cache not ready, unable to get joints meta.'
            self.logger.error(msg)
            raise CacheNotReadyError(msg)
        if self.joints_meta_reader is None:
            msg = 'joints_meta_reader not configured during construction, ' +\
                'unable to get joints meta.'
            self.logger.error(msg)
            raise CacheNotReadyError(msg)
        if joints_name in self.joints_files_paths:
            joints_path = self.joints_files_paths[joints_name]
            with open(joints_path, 'rb') as f:
                joints_bytes = f.read()
            return joints_bytes
        msg = f'No joints meta data record found for name={joints_name}.'
        self.logger.error(msg)
        raise KeyError(msg)

    async def get_rigids_meta_by_name(self, rigids_name: str) -> bytes:
        """Get rigids meta by name.

        Args:
            rigids_name (str): Name of the rigids.

        Returns:
            bytes: Rigids meta data.

        Raises:
            CacheNotReadyError: If cache is not ready or rigids meta reader is not
                configured.
            KeyError: If rigids name is not found.
        """
        if not self.cache_ready:
            msg = 'Cache not ready, unable to get rigids meta.'
            self.logger.error(msg)
            raise CacheNotReadyError(msg)
        if self.rigids_meta_reader is None:
            msg = 'rigids_meta_reader not configured during construction, ' +\
                'unable to get rigids meta.'
            self.logger.error(msg)
            raise CacheNotReadyError(msg)
        if rigids_name in self.rigids_files_paths:
            rigids_path = self.rigids_files_paths[rigids_name]
            with open(rigids_path, 'rb') as f:
                rigids_bytes = f.read()
            return rigids_bytes
        msg = f'No rigids meta data record found for name={rigids_name}.'
        self.logger.error(msg)
        raise KeyError(msg)

    async def get_blendshapes_meta_by_name(self, blendshapes_name: str) -> bytes:
        """Get blendshapes meta by name.

        Args:
            blendshapes_name (str): Name of the blendshapes.

        Returns:
            bytes: Blendshapes meta data.

        Raises:
            CacheNotReadyError: If cache is not ready or blendshapes meta reader is not
                configured.
            KeyError: If blendshapes name is not found.
        """
        if not self.cache_ready:
            msg = 'Cache not ready, unable to get blendshapes meta.'
            self.logger.error(msg)
            raise CacheNotReadyError(msg)
        if self.blendshapes_meta_reader is None:
            msg = 'blendshapes_meta_reader not configured during construction, ' +\
                'unable to get blendshapes meta.'
            self.logger.error(msg)
            raise CacheNotReadyError(msg)
        if blendshapes_name in self.blendshapes_files_paths:
            blendshapes_path = self.blendshapes_files_paths[blendshapes_name]
            with open(blendshapes_path, 'rb') as f:
                blendshapes_bytes = f.read()
            return blendshapes_bytes
        msg = f'No blendshapes meta data record found for name={blendshapes_name}.'
        self.logger.error(msg)
        raise KeyError(msg)

    async def get_motion_keywords(self) -> set[str]:
        """Get motion keywords.

        Returns:
            set[str]: Set of motion keywords.
        """
        return self.motion_keywords

    async def _sync_from_meta_reader(self) -> None:
        """Sync data from meta_reader to local cache."""
        # sync meta
        start_time = time.time()
        motion_records = dict()
        avatar_mapping = dict()
        motion_keywords = set()
        motion_record_ids = await self.meta_reader.get_ids()
        for motion_record_id in motion_record_ids:
            meta_dict = await self.meta_reader.get_meta_by_id(
                motion_record_id)
            if meta_dict['states'] is not None:
                motion_records[motion_record_id] = meta_dict
                avatar_name = meta_dict['avatar_name']
                if avatar_name not in avatar_mapping:
                    avatar_mapping[avatar_name] = set()
                avatar_mapping[avatar_name].add(motion_record_id)
            motion_keyword = meta_dict.get('motion_keyword', None)
            if motion_keyword is not None:
                for keyword in motion_keyword['motion_keywords_ch']:
                    motion_keywords.add(keyword)

        # set attrs
        self.motion_records = motion_records
        self.avatar_mapping = avatar_mapping
        self.motion_keywords = motion_keywords
        self.logger.info(
            f'Meta data sync completed, {len(motion_records)} records, ' +\
            f'time taken: {time.time() - start_time:.2f}s')

    async def _sync_from_motion_reader(self) -> None:
        """Sync data from motion_reader to local cache."""
        start_time = time.time()
        motion_record_ids = list(self.motion_records.keys())
        motion_clips_paths = dict()
        loop = asyncio.get_running_loop()
        for motion_record_id in motion_record_ids:
            motion_clip = await self.motion_reader.get_motion_clip_by_id(
                motion_record_id)
            npz_path = os.path.join(self.motion_clips_dir.name,
                                     f'{motion_record_id:08d}.npz')
            npz_io = await loop.run_in_executor(
                self.executor,
                motion_clip.to_npz)
            with open(npz_path, 'wb') as f:
                f.write(npz_io.getvalue())
            motion_clips_paths[motion_record_id] = npz_path
        # set attrs
        self.motion_clips_paths = motion_clips_paths
        self.logger.info(
            f'Motion data sync completed, {len(motion_clips_paths)} records, ' +\
            f'time taken: {time.time() - start_time:.2f}s')

    async def _sync_from_restpose_reader(self) -> None:
        """Sync data from restpose_reader to local cache."""
        start_time = time.time()
        restpose_paths = dict()
        restpose_names = await self.restpose_reader.get_file_keys()
        for restpose_name in restpose_names:
            restpose = await self.restpose_reader.get_file_by_key(
                restpose_name)
            npz_path = os.path.join(self.restpose_files_dir.name,
                                    f'{restpose_name}.npz')
            with open(npz_path, 'wb') as f:
                f.write(restpose)
            restpose_paths[restpose_name] = npz_path
        # set attrs
        self.restpose_paths = restpose_paths
        self.logger.info(
            f'Restpose data sync completed, {len(restpose_paths)} records, ' +\
            f'time taken: {time.time() - start_time:.2f}s')

    async def _sync_from_mesh_reader(self) -> None:
        """Sync data from mesh_reader to local cache."""
        start_time = time.time()
        mesh_paths = dict()
        mesh_names = await self.mesh_reader.get_file_keys()
        for mesh_name in mesh_names:
            mesh_bytes = await self.mesh_reader.get_file_by_key(mesh_name)
            mesh_path = os.path.join(self.mesh_files_dir.name,
                                     f'{mesh_name}.glb')
            with open(mesh_path, 'wb') as f:
                f.write(mesh_bytes)
            mesh_paths[mesh_name] = mesh_path
        # set attrs
        self.mesh_files_paths = mesh_paths
        self.logger.info(
            f'Mesh data sync completed, {len(mesh_paths)} records, ' +\
            f'time taken: {time.time() - start_time:.2f}s')

    async def _sync_from_joints_meta_reader(self) -> None:
        """Sync data from joints_meta_reader to local cache."""
        start_time = time.time()
        joints_paths = dict()
        joints_file_names = await self.joints_meta_reader.get_file_keys()
        for joints_file_name in joints_file_names:
            joints_bytes = await self.joints_meta_reader.get_file_by_key(
                joints_file_name)
            joints_path = os.path.join(self.joints_files_dir.name,
                                     f'{joints_file_name}.json')
            with open(joints_path, 'wb') as f:
                f.write(joints_bytes)
            joints_paths[joints_file_name] = joints_path
        # set attrs
        self.joints_files_paths = joints_paths
        self.logger.info(
            f'Joints data sync completed, {len(joints_paths)} records, ' +\
            f'time taken: {time.time() - start_time:.2f}s')

    async def _sync_from_rigids_meta_reader(self) -> None:
        """Sync data from rigids_meta_reader to local cache."""
        start_time = time.time()
        rigids_paths = dict()
        rigids_file_names = await self.rigids_meta_reader.get_file_keys()
        for rigids_file_name in rigids_file_names:
            rigids_bytes = await self.rigids_meta_reader.get_file_by_key(
                rigids_file_name)
            rigids_path = os.path.join(self.rigids_files_dir.name,
                                     f'{rigids_file_name}.json')
            with open(rigids_path, 'wb') as f:
                f.write(rigids_bytes)
            rigids_paths[rigids_file_name] = rigids_path
        # set attrs
        self.rigids_files_paths = rigids_paths
        self.logger.info(
            f'Rigids data sync completed, {len(rigids_paths)} records, ' +\
            f'time taken: {time.time() - start_time:.2f}s')

    async def _sync_from_blendshapes_meta_reader(self) -> None:
        """Sync data from blendshapes_meta_reader to local cache."""
        start_time = time.time()
        blendshapes_paths = dict()
        blendshapes_file_names = await self.blendshapes_meta_reader.get_file_keys()
        for blendshapes_file_name in blendshapes_file_names:
            blendshapes_bytes = await self.blendshapes_meta_reader.get_file_by_key(
                blendshapes_file_name)
            blendshapes_path = os.path.join(self.blendshapes_files_dir.name,
                                     f'{blendshapes_file_name}.json')
            with open(blendshapes_path, 'wb') as f:
                f.write(blendshapes_bytes)
            blendshapes_paths[blendshapes_file_name] = blendshapes_path
        # set attrs
        self.blendshapes_files_paths = blendshapes_paths
        self.logger.info(
            f'Blendshapes data sync completed, {len(blendshapes_paths)} records, ' +\
            f'time taken: {time.time() - start_time:.2f}s')

    async def _setup_motion_clips_cache(self) -> None:
        """Setup motion clips cache."""
        self.motion_clips_cache = dict()
        for motion_record_id in self.motion_records:
            meta_dict = self.motion_records[motion_record_id]
            if meta_dict['is_idle_long'] is not None:
                npz_path = self.motion_clips_paths[motion_record_id]
                loop = asyncio.get_running_loop()
                motion_clip = await loop.run_in_executor(
                    self.executor,
                    _load_motion_clip, npz_path)
                self.motion_clips_cache[motion_record_id] = motion_clip


def _load_motion_clip(npz_path: str) -> MotionClip:
    with open(npz_path, 'rb') as f:
        npz_io = io.BytesIO(f.read())
        npz_io.seek(0)
    motion_clip = MotionClip.from_npz(npz_io)
    return motion_clip

def _load_restpose(npz_path: str, name_override: None | str = None) -> Restpose:
    with open(npz_path, 'rb') as f:
        npz_io = io.BytesIO(f.read())
        npz_io.seek(0)
    return Restpose.from_npz(npz_io, name_override=name_override)
