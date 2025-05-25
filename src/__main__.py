"""
Main entry point for the gastronomy voice assistant application.
Initializes and runs the voice assistant.
"""

import argparse
import asyncio
import os

from agents import Runner
from dotenv import load_dotenv

# Import the main agent
from .agents_def.main_gastronomy_agent import gastronomy_agent

# Import the logger
from .core.logger_config import logger
from .core.voice_pipeline import setup_voice_pipeline


async def run_text_mode():
    """Run the assistant in text mode for testing without voice."""

    logger.info('\n==== Gastronomy Assistant (Text Mode) ====')
    logger.info("Type your message or 'quit' to exit.")

    while True:
        user_input = input('\nYou: ')
        if user_input.lower() in ['quit', 'exit', 'q']:
            logger.info('Exiting text mode...')
            break

        try:
            result = await Runner.run(gastronomy_agent, user_input)
            if result:
                logger.info('\nAssistant: %s', result.final_output)
            else:
                logger.info("\nAssistant: I'm sorry, I couldn't process that.")
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.exception('\nError in text mode: %s', str(e))


async def run_voice_mode():
    """Run the assistant in voice mode with STT and TTS."""
    voice_pipeline = setup_voice_pipeline(gastronomy_agent)

    logger.info('\n==== Gastronomy Voice Assistant ====')
    logger.info('Starting voice interaction mode...')
    logger.info('Speak to the assistant or press Ctrl+C to exit.')

    try:
        await voice_pipeline.start_interactive_session()
    except KeyboardInterrupt:
        logger.info('\nStopping voice assistant...')
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.exception('\nError in voice pipeline: %s', str(e))


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description='Gastronomy Voice Assistant')
    parser.add_argument(
        '--mode',
        choices=['text', 'voice'],
        default='text',
        help="Run mode: 'text' for text-only interaction or 'voice' for voice interaction",
    )

    args = parser.parse_args()

    if args.mode == 'voice':
        asyncio.run(run_voice_mode())
    else:
        asyncio.run(run_text_mode())


if __name__ == '__main__':
    # Load environment variables from .env file
    load_dotenv()

    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        logger.error(
            'OPENAI_API_KEY environment variable is not set. Please set it in the .env file.'
        )
        raise OSError(
            'OPENAI_API_KEY environment variable is not set. Please set it in the .env file.'
        )
    logger.info('OPENAI_API_KEY found.')

    main()
