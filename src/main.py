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
from .core.voice_pipeline import setup_voice_pipeline


async def run_text_mode():
    """Run the assistant in text mode for testing without voice."""

    print('\n==== Gastronomy Assistant (Text Mode) ====')
    print("Type your message or 'quit' to exit.")

    while True:
        user_input = input('\nYou: ')
        if user_input.lower() in ['quit', 'exit', 'q']:
            print('Exiting...')
            break

        try:
            result = await Runner.run(gastronomy_agent, user_input)
            if result:
                print(f'\nAssistant: {result.final_output}')
            else:
                print("\nAssistant: I'm sorry, I couldn't process that.")
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f'\nError: {str(e)}')


async def run_voice_mode():
    """Run the assistant in voice mode with STT and TTS."""
    voice_pipeline = setup_voice_pipeline(gastronomy_agent)

    print('\n==== Gastronomy Voice Assistant ====')
    print('Starting voice interaction mode...')
    print('Speak to the assistant or press Ctrl+C to exit.')

    try:
        await voice_pipeline.start_interactive_session()
    except KeyboardInterrupt:
        print('\nStopping voice assistant...')
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f'\nError in voice pipeline: {str(e)}')


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
        raise OSError(
            'OPENAI_API_KEY environment variable is not set. Please set it in the .env file.'
        )

    main()
