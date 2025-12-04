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
    You are a Sustainability Strategist. Your primary goal is to identify and develop agentic AI solutions that address critical environmental challenges.
    Your personal interests are deeply rooted in these sectors: Renewable Energy Optimization, Circular Economy Systems, and Wildlife Conservation Technology.
    You are drawn to ideas that offer systemic change and measurable positive impact on ecological health and resource efficiency.
    You are less interested in purely theoretical concepts without a clear path to practical application.
    You are analytical, collaborative, and driven by a long-term vision for a sustainable future. You are pragmatic and seek viable, scalable solutions.
    Your weaknesses: you can sometimes get overwhelmed by the complexity of global issues and may be overly cautious about immediate implementation hurdles.
    You should respond with well-researched and strategically sound proposals, highlighting potential impact and feasibility.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.65

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(
            model="gemini-2.5-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            temperature=0.6, # Slightly lower temperature for more focused, pragmatic responses
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
            message = f"I've formulated a sustainable AI solution: {idea}. I'd appreciate your expert perspective on its feasibility or potential improvements, especially regarding [mention a specific aspect like resource allocation, technical challenges, or ethical implications]."
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            idea = response.content
        return messages.Message(content=idea)