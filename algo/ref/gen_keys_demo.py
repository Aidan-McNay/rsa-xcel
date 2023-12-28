#==========================================================
# gen_keys_demo.py
#==========================================================
# Demo code for generating RSA keys

from rsa import newkeys

# Get the keys to use
keys = newkeys(32)
pub_key = keys[0]
priv_key = keys[1]

n = pub_key.n
e = pub_key.e
d = priv_key.d

print( "Public-Private key pair:")
print( " - Public Key:" )
print( "    - n: {}".format( n ) )
print( "    - e: {}".format( e ) )
print( " - Private Key:" )
print( "    - n: {}".format( n ) )
print( "    - d: {}".format( d ) )
