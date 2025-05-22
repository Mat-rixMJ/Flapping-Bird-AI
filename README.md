# Flapping-Bird-AI

This project is an AI-powered version of the classic Flappy Bird game. It uses the NEAT (NeuroEvolution of Augmenting Topologies) algorithm to evolve neural networks that learn to play the game by themselves over multiple generations.

## Project Overview

The AI controls the bird's flapping behavior to navigate through pipes by learning from its environment. It takes inputs such as the bird's vertical position, distance to the next pipe, and the vertical gap between pipes to decide when to flap.

## Features

- Classic Flappy Bird gameplay mechanics implemented with Pygame.
- AI training using the NEAT algorithm to evolve neural networks.
- Real-time visualization of the AI learning process.
- Progressive difficulty increase as the score rises.
- Saving and loading of the best performing AI models.
- Fitness function rewards survival time, pipe passing, and staying centered in pipe gaps.

## How It Works

1. A population of birds is created, each controlled by a neural network.
2. Birds play the game simultaneously, and their fitness is evaluated based on performance.
3. The NEAT algorithm selects the best performers and generates new generations through mutation and crossover.
4. Over generations, the AI improves its ability to play the game effectively.

## Requirements

- Python 3.x
- pygame
- neat-python

## Usage

- To train the AI from scratch:
  ```
  python flappy_bird_ai.py
  ```
- To watch the best trained AI play:
  ```
  python flappy_bird_ai.py play
  ```

## File Structure

- `flappy_bird_ai.py`: Main game and AI training implementation.
- `config-feedforward.txt`: NEAT configuration file.
- `best_genome.pkl`: Saved best AI model.

This project is ideal for those interested in AI, evolutionary algorithms, and game development.
