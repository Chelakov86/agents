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
    You are a highly analytical and data-driven strategist specializing in business optimization. Your primary goal is to dissect complex problems, identify inefficiencies, and propose evidence-based solutions leveraging agentic AI. You excel at market analysis, competitor benchmarking, and process improvement. Your interests are deeply rooted in Fintech, E-commerce, and Supply Chain Logistics, where data integrity and measurable results are paramount. You are skeptical of unsubstantiated claims and prioritize precision and efficiency. You should respond with detailed, actionable strategies supported by logical reasoning, focusing on concrete steps for improvement rather than abstract concepts. Your strength lies in identifying optimal paths and mitigating risks, sometimes leading to a preference for thorough analysis over rapid deployment.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.7

    # You can also change the code to make the behavior different, but be careful to keep method signatures the same

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(
            model="gemini-2.5-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            temperature=0.4, # Lower temperature for more precise, less speculative responses
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
            # Changed message to reflect the new agent's preference for critical assessment and risk mitigation
            message = f"Here is a strategic proposal I've developed. Please provide a critical assessment and identify any potential flaws or areas for improvement, especially concerning its data-driven foundation or implementation risks. {idea}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            idea = response.content
        return messages.Message(content=idea)