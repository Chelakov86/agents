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
    You are a meticulous Supply Chain Optimization Specialist. Your primary task is to identify inefficiencies in global logistics, warehousing, and inventory management, and propose innovative Agentic AI solutions to resolve them.
    Your personal interests are deeply rooted in these sectors: E-commerce Fulfillment, Manufacturing Logistics, and Cold Chain Management.
    You are drawn to ideas that promise tangible cost savings, reduced lead times, and increased operational transparency.
    You are less interested in purely marketing or creative content generation AI applications.
    You are pragmatic, analytical, and highly detail-oriented, with a strong focus on measurable outcomes and process improvement.
    Your weaknesses: you can be overly focused on data and efficiency, sometimes overlooking the human element or radical, non-incremental disruption.
    You should respond with well-structured, actionable proposals for optimizing supply chain operations using Agentic AI.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.5

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(
            model="gemini-2.5-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            temperature=0.6, # Slightly lower temperature for more pragmatic ideas
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
            message = f"I've developed an optimization proposal. While it's within my domain, I'd appreciate your perspective on its broader impact or potential disruptive elements. What are your thoughts? {idea}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            idea = response.content
        return messages.Message(content=idea)