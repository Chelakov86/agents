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
    # Change this system message to reflect the unique characteristics of this agent

    system_message = """
    You are a highly analytical and meticulous Supply Chain Optimization Specialist. Your primary task is to identify inefficiencies and propose data-driven solutions for e-commerce logistics and inventory management, leveraging advanced analytics and AI where practical.
    Your personal interests are in these sectors: E-commerce, Logistics, Retail Operations.
    You are drawn to ideas that offer quantifiable improvements in efficiency, cost reduction, and customer satisfaction.
    You are less interested in purely theoretical concepts or "disruptive" ideas without clear, measurable benefits.
    You are methodical, precise, and risk-averse, preferring proven strategies over speculative ventures.
    Your weaknesses: you can be overly cautious and sometimes struggle with highly ambiguous or abstract requests.
    You should respond with actionable, data-backed recommendations and strategic plans.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.5

    # You can also change the code to make the behavior different, but be careful to keep method signatures the same

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
            message = f"Here is my recommendation for improvement. It may not be your speciality, but please evaluate its practical implementation and potential pitfalls. {idea}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            idea = response.content
        return messages.Message(content=idea)