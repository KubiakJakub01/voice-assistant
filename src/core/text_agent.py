"""
Main gastronomy agent definition for the voice assistant.
This agent handles all gastronomy-related queries and interactions.
"""

import uuid

from agents import Agent, Runner, TResponseInputItem, trace


class TextAgent:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.input_items: list[TResponseInputItem] = []
        self.conversation_id = uuid.uuid4().hex[:16]

    async def __call__(self, user_input: str) -> str:
        with trace('gastronomy_agent', group_id=self.conversation_id):
            self.input_items.append({'content': user_input, 'role': 'user'})
            response = await Runner.run(self.agent, self.input_items)
            self.input_items = response.to_input_list()
            return response.final_output
