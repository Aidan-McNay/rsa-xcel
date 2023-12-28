#==========================================================
# encrypt_demo.py
#==========================================================
# Demo code for encrypting messages

from rsa.core import encrypt_int

# Get Input

print( "Inputting Public Key..." )
n = int( input( " n? : " ) )
e = int( input( " e? : " ) )

message = input( "\nMessage?\n" )
message_chars     = [ char        for char in message ]
message_char_nums = [ ord( char ) for char in message ]

# Encrypt Data

encrypted_data = []
for i in range( len( message_char_nums ) ):
    encrypted_data.append( encrypt_int( message_char_nums[i], e, n ) )

# Convert data to strings
message_char_nums = [ str( num ) for num in message_char_nums ]
encrypted_data    = [ str( num ) for num in encrypted_data    ]

# Print Data
message_display     = "Message:   "
message_num_display = "Values:    "
encrypted_display   = "Encrypted: "

for i in range( len( message_chars ) ):
    char        = message_chars[i]
    num         = message_char_nums[i]
    encrypt_num = encrypted_data[i]

    max_len = max( len( char ), len( num ), len( encrypt_num ) )

    # Append to display strings

    message_display     += (        char + ( " " * ( max_len - len(        char ) ) ) )
    message_num_display += (         num + ( " " * ( max_len - len(         num ) ) ) )
    encrypted_display   += ( encrypt_num + ( " " * ( max_len - len( encrypt_num ) ) ) )

    if( i != ( len( message_chars ) - 1 ) ): # Not the final element
        message_display     += " | "
        message_num_display += " | "
        encrypted_display   += " | "

print( "" )
print( message_display )
print( message_num_display )
print( encrypted_display )