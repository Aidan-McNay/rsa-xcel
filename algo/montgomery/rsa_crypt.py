#==========================================================
# rsa_crypt.py
#==========================================================
# Functions for encrypting and decrypting RSA messages

import math

#------------------------------------------
# MontMultiplier
#------------------------------------------
# Defines a Montgomery Multiplier for
# holding the key parameters for 
# Montgomery Multiplication

class MontMultiplier:

    def __init__( self, mod, R ):
        '''
        Here, R is the key parameter from montgomery multiplication, and
        mod is the modulus we perform multiplication under
        '''

        # Assert preconditions on values
        assert R > mod
        assert math.gcd( mod, R ) == 1

        # Assert that R is a power of 2
        assert ( R & ( R - 1 ) == 0 ) and ( R != 0 )

        # Store values
        self.R   = R
        self.mod = mod

        self.mask = ( R - 1 ) # Used for masking results to compute mod R

        # Compute number of bits to shift by for computing /R
        self.num_bits = 0
        while( R != 1 ):
            R = R >> 1
            self.num_bits += 1

        # Compute R^{-1} and N' with the Extended Euclid Algorithm

        #     new       old
        r = [ self.R, self.mod,   0 ]
        s = [      1,        0,   0 ]
        t = [      0,        1,   0 ]

        while( r[0] != 0 ):

            # Update values

            quotient = int( r[1]/r[0] )

            r = [ r[1] - ( quotient * r[0] ), r[0] ]
            s = [ s[1] - ( quotient * s[0] ), s[0] ]
            t = [ t[1] - ( quotient * t[0] ), t[0] ]

        self.R_reciprocal = s[1]
        self.N_reciprocal = -1 * t[1]

        # while( self.R_reciprocal < 0 ):
        #     print( "testing...")
        #     self.R_reciprocal += self.mod
        #     self.N_reciprocal += self.R

        # Lastly, we can pre-calculate R^2 (mod N) for ease of
        # converting numbers into N-residue format

        self.convert_in_factor = ( self.R ** 2 ) % self.mod

    def multiply( self, a, b ):
        '''
        Performs an instance of Montgomery multiplication

        Assumes that a and b are in N-residue form, and computes the output
        in the same form
        '''
        product = a * b

        # Use Montgomery Reduction of the product as defined in his paper

        m = ( ( product & self.mask ) * self.N_reciprocal ) & self.mask
        t = ( product + ( m * self.mod ) ) >> self.num_bits
        if( t >= self.mod ):
            t = t - self.mod
        
        return t
    
    def convert_in( self, x ):
        '''
        Converts a number into N-residue format

        Returns: x' = xR (mod N)

        Note that this is the same as performing Mont. multiplication 
        of x and ( R^2 (mod N) ), where the latter can be pre-computed
        '''

        return self.multiply( x, self.convert_in_factor )
    
    def convert_out( self, x_prime ):
        '''
        Converts a number out of N-residue format

        Returns: x = x'R^{-1} (mod N)

        Note that this is the same as performing Mont. multiplication
        of x and 1
        '''

        return self.multiply( x_prime, 1 )
    
    def __str__( self ):
        '''
        String representation (for debugging)
        '''

        string_repr =  "MontMult Instance\n"
        string_repr += " - R:         {}\n".format( self.R )
        string_repr += " - N:         {}\n".format( self.mod )
        string_repr += " - R^{{-1}}:    {}\n".format( self.R_reciprocal )
        string_repr += " - N':        {}\n".format( self.N_reciprocal )
        string_repr += " - R^2 mod N: {}\n".format( self.convert_in_factor )
        string_repr += " - num_bits:  {}\n".format( self.num_bits )
        return string_repr


#------------------------------------------
# mod_exp
#------------------------------------------
# Computes ( base ** exponent ) % modulus
# using modular exponentiation

def mod_exp( base, exponent, modulus ):

    # Adapted from Schneier, Bruce (1996). Applied Cryptography: Protocols, Algorithms, and Source Code in C, Second Edition (2nd ed.)
    # Using Montgomery multiplication

    result = 1
    base = base % modulus

    # Set up Montgomery multiplier

    MontMult = MontMultiplier( modulus, ( 1 << 32 ) )
    
    result = MontMult.convert_in( result )
    base   = MontMult.convert_in( base )

    while( exponent > 0 ):

        if( ( exponent % 2 ) == 1 ):
            result = MontMult.multiply( result, base )
        
        exponent = exponent >> 1
        base = MontMult.multiply( base, base )

    # Convert out of N-residue format
    result = MontMult.convert_out( result )
    
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

