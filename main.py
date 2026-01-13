"""
PyVenture: The Code Warrior
============================
An educational 2D top-down RPG where kids learn Python by typing code!

Control the hero by typing commands like:
    hero.move_right()
    hero.move_left()
    hero.move_up()
    hero.move_down()

Press F5 to reset, ESC to quit.
"""

from game import Game


def main() -> None:
    """Entry point for PyVenture."""
    print("=" * 50)
    print("  PyVenture: The Code Warrior")
    print("  Learn Python by playing!")
    print("=" * 50)
    print()
    print("Starting game...")
    print()
    
    # Create and run the game
    game = Game()
    game.run()
    
    print()
    print("Thanks for playing PyVenture!")
    print("Keep coding and learning!")


if __name__ == "__main__":
    main()
