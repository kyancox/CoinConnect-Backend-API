from master import master
from cb_sec import coinbase
from gemini_sec import gemini
from ledger_sec import ledger

# Checks if user input is a valid integer, and converts input from string to integer.  
def read_valid_int(prompt, min, max):

    userInput = input(prompt)
    if userInput.isdigit():
        value = int(userInput)
        if value >= min and value <= max:
            return value
    # If input is not a digit within min and max, the return message prompts the user to try again.
    return read_valid_int(f"Please enter your choice as an integer between {min} and {max}: ", min, max) 

def main():
    print("""====================================================
          
1) Show Master Portfolio
2) Show Coinbase Portfolio
3) Show Gemini Portfolio
4) Show Ledger Portfolio
5) Export Portfolios to Excel
6) Exit
          
          """)
    input = read_valid_int("Choose an option: ", 1, 6)
    print("\n====================================================\n")

    match input:
        case 1:
            master.showAssets()
        case 2:
            coinbase.showAssets()
        case 3:
            gemini.showAssets()
        case 4:
            ledger.showAssets()
        case 5:
            master.pandasToExcel_local()
        case 6:
            return
        
    main()

main()
    