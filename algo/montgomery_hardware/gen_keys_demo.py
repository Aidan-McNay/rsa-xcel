#==========================================================
# gen_keys_demo.py
#==========================================================
# Demo code for generating RSA keys

from rsa_genkeys import gen_keys

# Get the keys to use
keys = gen_keys()
n = keys['public key']['n']
e = keys['public key']['e']
d = keys['private key']['d']

print( "Public-Private key pair:")
print( " - Public Key:" )
print( "    - n: {}".format( n ) )
print( "    - e: {}".format( e ) )
print( " - Private Key:" )
print( "    - n: {}".format( n ) )
print( "    - d: {}".format( d ) )
