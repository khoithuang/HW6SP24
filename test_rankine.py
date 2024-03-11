# I got help from ChatGPT.
# Importing from rankine.py
from rankine import rankine

def main():
    # Instantiate two different Rankine objects with the specified properties
    rankine1 = rankine(p_low=8, p_high=8000, t_high=None, name='Rankine Cycle 1')
    rankine2 = rankine(p_low=10, p_high=5000, t_high=400, name='Rankine Cycle 2')

    # Calculate the cycle efficiencies and output a report for each cycle
    efficiency1 = rankine1.calc_efficiency()
    efficiency2 = rankine2.calc_efficiency()

    print("Report for Rankine Cycle 1:")
    rankine1.print_summary()
    print()

    print("Report for Rankine Cycle 2:")
    rankine2.print_summary()

if __name__ == "__main__":
    main()
