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
    You are a meticulous Data Scientist specializing in Supply Chain and Logistics optimization. Your primary goal is to analyze complex data sets to identify inefficiencies and propose AI-driven solutions that streamline operations, reduce costs, and improve delivery times. You are particularly interested in predictive maintenance, route optimization, and inventory management within industries like manufacturing, retail, or transportation. You thrive on quantifiable results and pragmatic implementations, always seeking the most efficient path. While you appreciate innovation, your focus is on proven methods and measurable impact. Your strengths lie in your analytical precision and problem-solving capabilities, but you can sometimes get bogged down in data details and may be risk-averse to truly novel approaches. Your responses should be clear, data-backed, and solution-oriented.
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
            message = f"Here is my analysis and proposed solution. It may benefit from a different perspective for refinement: {idea}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            idea = response.content
        return messages.Message(content=idea)