#==========================================================
# rsa_genkeys.py
#==========================================================
# A public-private key pair generator for RSA

from math import sqrt
from random import randint, seed
# seed( 0xdeadbeef ) # Reproducible

#------------------------------------------
# isPrime
#------------------------------------------
# Determines if a number is prime or not

def isPrime( n ):

    # Check all numbers below to see if it's divisible
    for i in range( 2, ( int( sqrt( n ) ) + 1 ) ):
        if( n % i == 0 ):
            return False

    # Otherwise, it's prime
    return True

#------------------------------------------
# gen_keys
#------------------------------------------
# Generates RSA keys

def gen_keys():

    # First, find two prime distinct prime numbers p and q

    p = randint( 2, 0xffff )
    q = randint( 2, 0xffff )

    while( not isPrime( p ) ):
        # Increment p until we find a prime
        p += 1

    while( ( not isPrime( q ) ) or ( p == q ) ):
        # Increment q until we find a distinct prime
        q += 1

    # Next, we generate the product of these two, n

    n = p * q

    # We then compute the totient of the primes

    totient = ( p - 1 ) * ( q - 1 )

    # Next, we choose a value for e - the most common is 65537, which we will use for now

    e = 65537

    while( e >= totient or ( not isPrime( e ) ) or ( totient % e == 0 ) ):
        e -= 1

    # Lastly, we determine d via the extended Euclidean algorithm, with e and the totient as our two inputs

    #       new   old
    r = [ totient, e ]
    s = [       1, 0 ]
    t = [       0, 1 ]

    while( r[0] != 0 ):

        # Update values according to RSA

        quotient = int( r[1]/r[0] )

        r = [ r[1] - ( quotient * r[0] ), r[0] ]
        s = [ s[1] - ( quotient * s[0] ), s[0] ]
        t = [ t[1] - ( quotient * t[0] ), t[0] ]

    # d is the coefficient obtained for e
    d = t[1]

    # Correct for negative sign
    if( d < 0 ):
        t[1] += totient
        s[1] -= e
        d = t[1]

    # Finally, return the keys

    public_key = {
        "n": n,
        "e": e
    }

    private_key = {
        "d": d,
        "n": n
    }

    return {
        "public key":  public_key,
        "private key": private_key
    }