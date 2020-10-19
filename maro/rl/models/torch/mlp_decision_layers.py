# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import torch.nn as nn


class MLPDecisionLayers(nn.Module):
    """NN model to compute state or action values.

    Fully connected network with batch normalization, leaky RELU and dropout as layer components.

    Args:
        name (str): Network name.
        input_dim (int): Network input dimension.
        hidden_dims ([int]): Network hidden layer dimension. The length of ``hidden_dims`` means the
                            hidden layer number, which requires larger than 1.
        output_dim (int): Network output dimension.
        dropout_p (float): Dropout parameter.
        softmax (bool): If true, the output of the net will be a softmax transformation of the top layer's output.
            Defaults to False.
    """
    def __init__(
        self, *, name: str, input_dim: int, output_dim: int, hidden_dims: [int], dropout_p: float,
        softmax: bool = False
    ):
        super().__init__()
        self._name = name
        self._input_dim = input_dim
        self._hidden_dims = hidden_dims if hidden_dims is not None else []
        self._output_dim = output_dim
        self._dropout_p = dropout_p
        self._layers = self._build_layers([input_dim] + self._hidden_dims)
        if len(self._hidden_dims) == 0:
            self._head = nn.Linear(self._input_dim, self._output_dim)
        else:
            self._head = nn.Linear(hidden_dims[-1], self._output_dim)
        self._net = nn.Sequential(*self._layers, self._head)
        self._softmax = nn.Softmax(dim=1) if softmax else None

    def forward(self, x):
        out = self._net(x).double()
        return self._softmax(out) if self._softmax else out

    @property
    def input_dim(self):
        return self._input_dim

    @property
    def name(self):
        return self._name

    @property
    def output_dim(self):
        return self._output_dim

    def _build_basic_layer(self, input_dim, output_dim):
        """Build basic layer.

        BN -> Linear -> LeakyReLU -> Dropout
        """
        return nn.Sequential(nn.BatchNorm1d(input_dim),
                             nn.Linear(input_dim, output_dim),
                             nn.LeakyReLU(),
                             nn.Dropout(p=self._dropout_p))

    def _build_layers(self, layer_dims: []):
        """Build multi basic layer.

        BasicLayer1 -> BasicLayer2 -> ...
        """
        layers = []
        for input_dim, output_dim in zip(layer_dims, layer_dims[1:]):
            layers.append(self._build_basic_layer(input_dim, output_dim))
        return layers