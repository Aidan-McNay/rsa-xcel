#==========================================================
# test.py
#==========================================================
# Tests our various algorithmic implementations using
# our reference

from rsa.core import encrypt_int, decrypt_int
from rsa      import newkeys

from naive.rsa_crypt      import encrypt as encrypt_naive
from naive.rsa_crypt      import decrypt as decrypt_naive

from montgomery.rsa_crypt import encrypt as encrypt_mont
from montgomery.rsa_crypt import decrypt as decrypt_mont
from montgomery_hardware.rsa_crypt import encrypt as encrypt_hard
from montgomery_hardware.rsa_crypt import decrypt as decrypt_hard

from random import randint, seed
seed( 0xdeadbeef )

def gen_keys( size ):
    '''
    Generates RSA keys of a given size
    '''

    keys = newkeys(32)
    pub_key = keys[0]
    priv_key = keys[1]

    n = pub_key.n
    e = pub_key.e
    d = priv_key.d

    return n, e, d

def test_encrypt( message, e, n ):
    '''
    Tests that all implementations encrypt a message the
    same way, and returns that message
    '''

    ref   = encrypt_int  ( message, e, n )
    naive = encrypt_naive( message, e, n )
    mont  = encrypt_mont ( message, e, n )
    hard  = encrypt_hard ( message, e, n )

    if( ( ref != naive ) or ( ref != mont ) or ( ref != hard ) ): # We don't agree
        print( "ERROR: Encryption doesn't agree!" )

        print( "Message:    {}".format( message ) )
        print( "n:          {}".format( n )       )
        print( "e:          {}".format( e )       )

        print( "Reference:  {}".format( ref )   )
        print( "Naive:      {}".format( naive ) )
        print( "Montgomery: {}".format( mont )  )

        assert False

    # Otherwise, they all agree
    return ref

def test_decrypt( ciphertext, d, n ):
    '''
    Tests that all implementations decrypt a message the
    same way, and returns that message
    '''

    ref   = encrypt_int  ( ciphertext, d, n )
    naive = encrypt_naive( ciphertext, d, n )
    mont  = encrypt_mont ( ciphertext, d, n )
    hard  = encrypt_hard ( ciphertext, d, n )

    if( ( ref != naive ) or ( ref != mont ) or ( ref != hard ) ): # We don't agree
        print( "ERROR: Decryption doesn't agree!" )

        print( "Ciphertext: {}".format( ciphertext ) )
        print( "n:          {}".format( n )          )
        print( "d:          {}".format( d )          )

        print( "Reference:  {}".format( ref )   )
        print( "Naive:      {}".format( naive ) )
        print( "Montgomery: {}".format( mont )  )

        assert False

    # Otherwise, they all agree
    return ref

if __name__ == "__main__":

    for i in range( 1000 ): # Run 100 tests
        
        # Generate keys
        n, e, d = gen_keys( 32 )

        # Generate a random message such that 0 <= M < n
        message = randint( 0, n - 1 )

        # Encrypt the message
        ciphertext = test_encrypt( message, e, n )

        # Decrypt the message
        new_message = test_decrypt( ciphertext, d, n )

        # Ensure that they're the same
        if( message != new_message ):
            print( "ERROR: Didn't get same message back!" )

            print( "n:              {}".format( n ) )
            print( "d:              {}".format( d ) )
            print( "d:              {}".format( d ) )

            print( "Message:        {}".format( message )    )
            print( "Ciphertext:     {}".format( ciphertext ) )
            print( "New message:    {}".format( message )    )

            assert False

        print( "Test {} passed".format( i ) )

    # If we got here, all tests passed
    print( "All tests passed!" )
