# Copyright 2018 DeepMind Technologies Limited. All rights reserved.
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

"""Base interfaces for networks."""

import dataclasses
from typing import Callable, Optional, Protocol, Tuple

from acme import types
from acme.jax import types as jax_types
import haiku as hk
import jax.numpy as jnp

# This definition is deprecated. Use jax_types.PRNGKey directly instead.
# TODO(sinopalnikov): migrate all users and remove this definition.
PRNGKey = jax_types.PRNGKey

# Commonly-used types.
Observation = types.NestedArray
Action = types.NestedArray
Params = types.NestedArray
NetworkOutput = types.NestedArray
QValues = jnp.ndarray
Logits = jnp.ndarray
LogProb = jnp.ndarray
Value = jnp.ndarray

# Commonly-used function/network signatures.
QNetwork = Callable[[Observation], QValues]
LSTMOutputs = Tuple[Tuple[Logits, Value], hk.LSTMState]
PolicyValueRNN = Callable[[Observation, hk.LSTMState], LSTMOutputs]
RecurrentQNetwork = Callable[[Observation, hk.LSTMState],
                             Tuple[QValues, hk.LSTMState]]
SampleFn = Callable[[NetworkOutput, PRNGKey], Action]
LogProbFn = Callable[[NetworkOutput, Action], LogProb]


@dataclasses.dataclass
class FeedForwardNetwork:
  """Holds a pair of pure functions defining a feed-forward network.

  Attributes:
    init: A pure function: ``params = init(rng, *a, **k)``
    apply: A pure function: ``out = apply(params, rng, *a, **k)``
  """
  # Initializes and returns the networks parameters.
  init: Callable[..., Params]
  # Computes and returns the outputs of a forward pass.
  apply: Callable[..., NetworkOutput]


class ApplyFn(Protocol):

  def __call__(self,
               params: Params,
               observation: Observation,
               *args,
               is_training: bool,
               key: Optional[PRNGKey] = None,
               **kwargs) -> NetworkOutput:
    ...


@dataclasses.dataclass
class TypedFeedForwardNetwork:
  """FeedForwardNetwork with more specific types of the member functions.

  Attributes:
    init: A pure function. Initializes and returns the networks parameters.
    apply: A pure function. Computes and returns the outputs of a forward pass.
  """
  init: Callable[[PRNGKey], Params]
  apply: ApplyFn


def non_stochastic_network_to_typed(
    network: FeedForwardNetwork) -> TypedFeedForwardNetwork:
  """Converts non-stochastic FeedForwardNetwork to TypedFeedForwardNetwork.

  Non-stochastic network is the one that doesn't take a random key as an input
  for its `apply` method.

  Arguments:
    network: non-stochastic feed-forward network.

  Returns:
    corresponding TypedFeedForwardNetwork
  """

  def apply(params: Params,
            observation: Observation,
            *args,
            is_training: bool,
            key: Optional[PRNGKey] = None,
            **kwargs) -> NetworkOutput:
    del is_training, key
    return network.apply(params, observation, *args, **kwargs)

  return TypedFeedForwardNetwork(init=network.init, apply=apply)
