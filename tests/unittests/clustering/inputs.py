# Copyright The Lightning team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from collections import namedtuple

import torch
from sklearn.datasets import make_blobs

from unittests import BATCH_SIZE, EXTRA_DIM, NUM_BATCHES, NUM_CLASSES
from unittests.helpers import seed_all

seed_all(42)


# extrinsic input for clustering metrics that requires predicted clustering labels and target clustering labels
ExtrinsicInput = namedtuple("ExtrinsicInput", ["preds", "target"])

# intrinsic input for clustering metrics that requires only predicted clustering labels and the cluster embeddings
IntrinsicInput = namedtuple("IntrinsicInput", ["data", "labels"])


def _batch_blobs(num_batches, num_samples, num_features, num_classes):
    data, labels = [], []
    for _ in range(num_batches):
        _data, _labels = make_blobs(num_samples, num_features, centers=num_classes)
        data.append(torch.tensor(_data))
        labels.append(torch.tensor(_labels))

    return IntrinsicInput(data=torch.stack(data), labels=torch.stack(labels))


_single_target_extrinsic1 = ExtrinsicInput(
    preds=torch.randint(high=NUM_CLASSES, size=(NUM_BATCHES, BATCH_SIZE)),
    target=torch.randint(high=NUM_CLASSES, size=(NUM_BATCHES, BATCH_SIZE)),
)

_single_target_extrinsic2 = ExtrinsicInput(
    preds=torch.randint(high=NUM_CLASSES, size=(NUM_BATCHES, BATCH_SIZE)),
    target=torch.randint(high=NUM_CLASSES, size=(NUM_BATCHES, BATCH_SIZE)),
)

_float_inputs_extrinsic = ExtrinsicInput(
    preds=torch.rand((NUM_BATCHES, BATCH_SIZE)), target=torch.rand((NUM_BATCHES, BATCH_SIZE))
)

# intrinsic input for clustering metrics that requires only predicted clustering labels and the cluster embeddings
_single_target_intrinsic1 = _batch_blobs(NUM_BATCHES, BATCH_SIZE, EXTRA_DIM, NUM_CLASSES)
_single_target_intrinsic2 = _batch_blobs(NUM_BATCHES, BATCH_SIZE, EXTRA_DIM, NUM_CLASSES)
