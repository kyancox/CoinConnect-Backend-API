from master import master
from cb import coinbase
from gemini import gemini
from ledger import ledger

# Checks if user input is a valid integer, and converts input from string to integer.  
def read_valid_int(prompt, min, max):

    userInput = input(prompt)
    if userInput.isdigit():
        value = int(userInput)
        if value >= min and value <= max:
            return value
        # For fun
        if value > 1000000:
            print("Please, 1please, please do not invest more than $1,000,000 at a time.")
    # If input is not a digit within min and max, the return message prompts the user to try again.
    return read_valid_int(f"Please enter your choice as an integer between {min} and {max}: ", min, max) 

def main():
    print("""====================================================
          
1) Show Master Portfolio
2) Show Coinbase Portfolio
3) Show Gemini Portfolio
4) Show Ledger Portfolio
5) Exit
6) Export Portfolios to Excel
          
          """)
    input = read_valid_int("Choose an option: ", 1, 5)
    print()

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
            return
        
    main()

main()
    