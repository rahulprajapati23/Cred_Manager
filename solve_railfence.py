def decrypt_rail_fence(cipher, depth=4):
    rail = [['\n' for i in range(len(cipher))]
            for j in range(depth)]
    
    dir_down = None
    row, col = 0, 0
    
    # Mark the places with '*'
    for i in range(len(cipher)):
        if row == 0:
            dir_down = True
        if row == depth - 1:
            dir_down = False
        
        rail[row][col] = '*'
        col += 1
        
        if dir_down:
            row += 1
        else:
            row -= 1
            
    # Fill the '*' with ciphertext characters
    index = 0
    for i in range(depth):
        for j in range(len(cipher)):
            if ((rail[i][j] == '*') and
               (index < len(cipher))):
                rail[i][j] = cipher[index]
                index += 1
                
    # Read the matrix in zig-zag manner to construct plaintext
    result = []
    row, col = 0, 0
    for i in range(len(cipher)):
        if row == 0:
            dir_down = True
        if row == depth - 1:
            dir_down = False
            
        if rail[row][col] != '*':
            result.append(rail[row][col])
            col += 1
            
        if dir_down:
            row += 1
        else:
            row -= 1
    return("".join(result))

if __name__ == "__main__":
    print("=== Rail Fence Cipher Solver ===")
    print("This tool helps you solve the Challenge from the Password Manager.")
    
    while True:
        ciphertext = input("\nEnter the Ciphertext (or 'q' to quit): ").strip()
        if ciphertext.lower() == 'q':
            break
            
        try:
            depth_input = input("Enter Depth (Press Enter for default 4): ").strip()
            depth = int(depth_input) if depth_input else 4
            
            plaintext = decrypt_rail_fence(ciphertext, depth)
            print(f"\nDECRYPTED: {plaintext}")
            print("-" * 30)
            
        except ValueError:
            print("Invalid depth. Please enter a number.")
        except Exception as e:
            print(f"Error: {e}")
