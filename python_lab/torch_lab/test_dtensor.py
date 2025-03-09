import pdb
import sys
import os
def log(msg):
    from datetime import datetime
    now = datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{now}: {msg}")

log("init")

def info2(type, value, tb):
    import time
    time.sleep(10000)

def bp():
    import ptvsd
    ptvsd.enable_attach(address=('0.0.0.0', 5678))
    ptvsd.wait_for_attach()

bp()
log("before torch")
import torch
log("before torch dist")
from torch.distributed._tensor import DTensor, DeviceMesh, Shard, Replicate, distribute_tensor, distribute_module
from typing import Optional, Tuple, Union

class DeviceMeshInner(DeviceMesh):
    def __init__(
        self,
        device_type: str,
        mesh: Union[torch.Tensor, "ArrayLike"],
        *,
        mesh_dim_names: Optional[Tuple[str, ...]] = None,
        _init_backend: bool = False
    ) -> None:
        super().__init__("xla", mesh, mesh_dim_names=mesh_dim_names, _init_backend=_init_backend)
        self.device_type = device_type

        # calculate the coordinates of the current global rank on the mesh
        rank_coords = (self.mesh == self.get_rank()).nonzero()
        assert rank_coords.size(0) in (0, 1)
        self._coordinate_on_dim: Optional[List[int]] = (
            rank_coords[0].tolist() if rank_coords.size(0) > 0 else None
        )

    def get_rank(self) -> int:
        return 0

log("before torch br")
# import torch_br
# from torch_br.contrib import transfer_to_supa

log("after torch br")

device_str = "cuda"
device_str = "cpu"

# construct a device mesh with available devices (multi-host or single host)
device_mesh = DeviceMeshInner(device_str, [0, 1, 2, 3])

# if we want to do row-wise sharding
rowwise_placement=[Shard(0)]
# if we want to do col-wise sharding
colwise_placement=[Shard(1)]

big_tensor = torch.randn(1, 888, 12)
# distributed tensor returned will be sharded across the dimension specified in placements
rowwise_tensor = DTensor.from_local(big_tensor, device_mesh=device_mesh, placements=rowwise_placement)
# rowwise_tensor2 = rowwise_tensor.relu()

# if we want to do replication across a certain device list
replica_placement = [Replicate()]
# distributed tensor will be replicated to all four GPUs.
replica_tensor = DTensor.from_local(big_tensor, device_mesh=device_mesh, placements=replica_placement, run_check=False)
res = rowwise_tensor + replica_tensor


# Another test
local_tensor = torch.randn((32, 4), requires_grad=True)

# if we want to distributed a tensor with both replication and sharding
device_mesh = DeviceMeshInner(device_str, [[0, 1], [2, 3]])
# replicate across the first dimension of device mesh, then sharding on the second dimension of device mesh
spec=[Shard(0), Replicate()]
shard_0_rep = DTensor.from_local(local_tensor, device_mesh=device_mesh, placements=spec, run_check=False)

local_tensor2 = torch.randn((4, 16), requires_grad=True)
spec2=[Replicate(), Shard(1)]
rep_shard_1 = DTensor.from_local(local_tensor2, device_mesh, placements=spec2, run_check=False)

res = torch.matmul(shard_0_rep, rep_shard_1)

log("after all")
