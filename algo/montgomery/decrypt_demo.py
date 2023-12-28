#==========================================================
# encrypt_demo.py
#==========================================================
# Demo code for decrypting messages

from rsa_crypt import decrypt

# Get Input

print( "Inputting Private Key..." )
n = int( input( " n? : " ) )
d = int( input( " d? : " ) )

print( "" )
print( "Encrypted Message?" )
print( " - Data values separated by '|', possibly including spaces")
data = input()

# Format data into pieces
data = [ int( datum.strip() ) for datum in data.split( "|" ) ]

# Decrypt the message

message_char_nums = []
message_chars     = []

for datum in data:
    result = decrypt( datum, d, n )
    message_char_nums.append( result )
    message_chars.append( chr( result ) )

# Convert data to strings
data              = [ str( num ) for num in data              ]
message_char_nums = [ str( num ) for num in message_char_nums ]

# Print Data
encrypt_display     = "Encrypted Data: "
message_num_display = "Decrypted Data: "
message_display     = "Characters:     "

for i in range( len( data ) ):
    encrypt_num  = data[i]
    decrypt_num  = message_char_nums[i]
    message_char = message_chars[i]

    max_len = max( len( encrypt_num ), len( decrypt_num ), len( message_char ) )

    # Append to display strings

    encrypt_display     += (  encrypt_num + ( " " * ( max_len - len(  encrypt_num ) ) ) )
    message_num_display += (  decrypt_num + ( " " * ( max_len - len(  decrypt_num ) ) ) )
    message_display     += ( message_char + ( " " * ( max_len - len( message_char ) ) ) )

    if( i != ( len( data ) - 1 ) ): # Not the final element
        encrypt_display     += " | "
        message_num_display += " | "
        message_display     += " | "

print( "" )
print( encrypt_display     )
print( message_num_display )
print( message_display     )
print( "" )
print( "Final Decrypted Message: \n{}".format( "".join( message_chars ) ) )