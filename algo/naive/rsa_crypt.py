#==========================================================
# rsa_crypt.py
#==========================================================
# Functions for encrypting and decrypting RSA messages

#------------------------------------------
# mod_exp
#------------------------------------------
# Computes ( base ** exponent ) % modulus
# using modular exponentiation

def mod_exp( base, exponent, modulus ):

    # Adapted from Schneier, Bruce (1996). Applied Cryptography: Protocols, Algorithms, and Source Code in C, Second Edition (2nd ed.)

    result = 1
    base = base % modulus

    while( exponent > 0 ):

        if( ( exponent % 2 ) == 1 ):
            result = ( result * base ) % modulus
        
        exponent = exponent >> 1
        base = ( base * base ) % modulus

    return result


#------------------------------------------
# encrypt
#------------------------------------------
# Encrypts a message using our public key

def encrypt( message, e, n ):

    if( message < 0 or message >= n ):
        print( "ERROR: You message doesn't follow 0 <= message < n. Try padding your message" )
        return

    ciphertext = mod_exp( message, e, n )
    return ciphertext

#------------------------------------------
# decrypt
#------------------------------------------
# Decrypt a message using our private key

def decrypt( ciphertext, d, n ):
    message = mod_exp( ciphertext, d, n )
    return message

