# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import torch.nn as nn
from torch.optim import RMSprop

from .agent import CIMAgent
from maro.rl import SimpleAgentManager, LearningModel, FullyConnectedNet, DQN, DQNHyperParams, ColumnBasedStore
from maro.utils import set_seeds


def create_dqn_agents(agent_id_list, config):
    num_actions = config.algorithm.num_actions
    set_seeds(config.seed)
    agent_dict = {}
    for agent_id in agent_id_list:
        q_value_model = LearningModel(
            FullyConnectedNet(
                name=f'{agent_id}.policy',
                input_dim=config.algorithm.input_dim,
                output_dim=num_actions,
                activation=nn.LeakyReLU,
                **config.algorithm.model
            )
        )

        algorithm = DQN(
            value_model=q_value_model,
            value_optimizer_cls=RMSprop,
            value_optimizer_params=config.algorithm.optimizer,
            loss_func=nn.functional.smooth_l1_loss,
            hyper_params=DQNHyperParams(
                **config.algorithm.hyper_parameters,
                num_actions=num_actions
            )
        )

        experience_pool = ColumnBasedStore(**config.experience_pool)
        agent_dict[agent_id] = CIMAgent(
            name=agent_id,
            algorithm=algorithm,
            experience_pool=experience_pool,
            **config.training_loop_parameters
        )

    return agent_dict


class DQNAgentManager(SimpleAgentManager):
    def train(self, experiences_by_agent, performance=None):
        self._assert_train_mode()

        # store experiences for each agent
        for agent_id, exp in experiences_by_agent.items():
            exp.update({"loss": [1e8] * len(list(exp.values())[0])})
            self.agent_dict[agent_id].store_experiences(exp)

        for agent in self.agent_dict.values():
            agent.train()
