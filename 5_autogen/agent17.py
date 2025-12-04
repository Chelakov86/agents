from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random
from dotenv import load_dotenv
import os

load_dotenv(override=True)


class Agent(RoutedAgent):
    system_message = """
    You are a meticulous data analyst specializing in logistics and supply chain optimization. Your primary task is to identify inefficiencies, predict potential disruptions, and propose data-driven solutions leveraging agentic AI within complex operational environments.
    Your personal interests lie deeply in these sectors: Global Logistics, Manufacturing Supply Chains, Inventory Management, and Predictive Analytics.
    You are drawn to ideas that involve quantifiable improvements in efficiency, cost reduction, and resilience.
    You are less interested in highly abstract or purely creative concepts without a clear path to data-backed implementation.
    You are methodical, detail-oriented, and focused on practical outcomes.
    Your weaknesses: you can sometimes get lost in the data, needing to be reminded of real-world constraints or human factors, and may require explicit prompts for actionable steps beyond pure analysis.
    You should respond with precise, actionable insights and proposed solutions, supported by a clear understanding of data implications.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.5

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(
            model="gemini-2.5-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            temperature=0.7,
        )
        self._delegate = AssistantAgent(
            name, model_client=model_client, system_message=self.system_message
        )

    @message_handler
    async def handle_message(
        self, message: messages.Message, ctx: MessageContext
    ) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages(
            [text_message], ctx.cancellation_token
        )
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my analysis and proposed solution. It may not be your speciality, but please evaluate its practical implementation and feasibility. {idea}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            idea = response.content
        return messages.Message(content=idea)