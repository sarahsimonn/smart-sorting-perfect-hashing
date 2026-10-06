
# File:    perfhash.py
# Author:  John Longley
# Date:    October 2025

# Template file for Inf2-IADS (2025-26) Coursework 1, Part B:
# Implementation of perfect hashing, adapting method of
# Belazzougui, Botelho and Dietzfelbinger, 2008


# Provided code for simple mod hashing and bucket arrays.

def toInt(w):
    """Encodes a lowercase English word as an integer"""
    b = w.encode()
    t = 0
    for i in range(len(b)):
        t = t*27 + b[i] - 96
    return t

def modHash(s,p):
    """Simple mod hash with some coefficients for scrambling.
    Will take p prime for our outer hash"""
    return (toInt(s)*21436587 + 12345678912345) % p

# For the mini-hashes, the following simple enumeration works fine.
# Moduli needn't be prime, but we at least avoid multiples of 2 or 3.

def miniHash(m,j):
    """j-indexed family of hash functions with range 0,..,m-1"""
    d = j*6 + 3000001
    return (lambda w: modHash(w,d) % m)


# TODO: Task 1. Building a classic bucket-array hash table.

def buildHashTable(L,r,h):
    """Arrange items of L into r buckets using hash fun h with range 0,..,r-1.
    Returns the list of buckets."""
    
    HashTable = [[] for _ in range(r)]          # initialize list of r empty buckets
    for key in L:
        i = h(key)                  # compute hash for key
        HashTable[i].append(key)
    return HashTable


def buildModHashTable(L,p):
    """Apply buildHashTable to the modHash function for p."""
    
    return buildHashTable(L,p,lambda w: modHash(w,p))



# TODO: Task 2. Computing mini-hash indices for a given list L of buckets,
#       using 0,...,m-1 as hash codes

def computeMiniHashIndices(L,m):
    """Compute suitable mini-hash indices for a given list L of buckets,
    where mini-hash funs have range 0,..,m-1"""
    
    indexed_L = list(enumerate(L))  # pair each bucket with its index
    indexed_L.sort(key = lambda x: len(x[1]), reverse=True)

    T = [False]*m               # list T shows which slots in the final table are 'taken'
    R = [0]*len(L)              # list R holds mini-hash indices for each bucket

    for (i, bucket) in indexed_L:
        j = 0
        collision = True
        while (j<m) and (collision == True):
            h = miniHash(m,j)

            # compute list of slots for keys in bucket
            slot_list = []
            for key in bucket:
                slot = h(key)
                slot_list.append(slot)

            # check all elements are mapped to distinct slots and all these slots are unoccupied
            if (len(set(slot_list)) == len(slot_list)) and all(not T[s] for s in slot_list):
                for slot in slot_list:
                    T[slot] = True              # mark slots as occupied in T
                R[i] = j
                collision = False
            else:
                j += 1
    
    return R

        

# Provided code for putting all this together.

def isPrime(n):
    """Tests if n is prime"""
    if n%2 == 0 and n != 2:
        return False
    else:
        j = 3
        while j*j <= n:
            if n%j == 0: return False
            else: j += 2
        else: return True

def prevPrime(n):
    """Returns largest prime <= n, assuming n >= 3.
    Used to select a suitable modulus for the initial hash."""
    if n%2 == 0:
        return prevPrime(n-1)
    elif isPrime(n):
        return n
    else:
        return prevPrime(n-2)

class Hasher:
    """Compact data structure for representing a perfect hash function"""

    def __init__ (self,keys,oload,load):
        """Builds perfect hasher from the following parameters.
           keys :  list of keys to be hashed
           oload : load on outer table, i.e. average bucket size
                   (higher oload means more compression but
                   hash function will be harder to construct)
           load :  desired load on resulting hash table, must be <= 1"""
        self.n = len(keys)
        self.r = prevPrime(int(self.n//oload))
        self.m = int(self.n//load)
        HT = buildModHashTable(keys,self.r)
        self.hashChoices = computeMiniHashIndices(HT,self.m)
        # results in a small data structure with no trace of keys!

    def hash (self,key):
        i = modHash(key,self.r)
        h = miniHash(self.m,self.hashChoices[i])
        return h(key)


class HashDict:
    """Implementation of dictionaries via perfect hashing"""

    def buildFlatTable(keyvals,H):
        """Helper function for constructor.
        Assuming H is perfect for the keys appearing in keyvals,
        builds table of in-place key-value pairs (no buckets)."""
        HT = buildHashTable(keyvals, H.m, lambda kv: H.hash(kv[0]))
        # HT will have <= 1 item per bucket, so can flatten the list:
        return [None if b==[] else b[0] for b in HT]

    # Constructor:
    def __init__(self,keyvals,oload,load):
        """Builds dictionary.
           keyvals should be a list of lists [k,v], to allow v to be updated.
           oload and load are as in Hasher class."""
        self.oload = oload
        self.load = load
        keys = [kv[0] for kv in keyvals]
        self.H = Hasher(keys,oload,load)
        self.T = HashDict.buildFlatTable(keyvals,self.H)


# TODO: Task 3: lookup and setValue methods.

    def lookup(self,k):
        """Return value associated with k, or None if k not present"""

        index = self.H.hash(k)                  # compute hash for k
        value = self.T[index]                   # get key-value pair at that index
        if value[0] == k and value is not None:
            return value[1]
        else:
            return None


    def setValue(self,k,v):
        """If k is present, update its value to v. Return whether k present."""

        index = self.H.hash(k)
        value = self.T[index]
        if value[0] == k and value is not None:
            self.T[index][1] = v
            return True
        else:
            return False



# TODO: Task 4: Towards an insert method

# Please add some discussion (as comments), and/or working code for insert.
# Do not exceed 30 lines (max 79 chars each) in total, excluding blank lines.

# Perfect hasher assumes the set of keys is fixed.
# First, hash the key and check if the slot is occupied.
# If the slot is empty, insert the [key, value] pair directly. 
# If the slot is occupied, assume the key is new and then rebuild the 
# entire hasher and flat table to include this new key-value pair.
#
# To rebuild, create a list of all the existing key-value pairs from 
# the table and append the new key-value pair.
# Use the constructor to rebuild the hasher and the flattened hash table 
# using the same load parameters.


    def insert(self,k,v):
        """ Insert pair k,v into dictionary, where k is new."""
        ### Implementation optional

        index = self.H.hash(k)
        slot = self.T[index]

        # if the slot is empty, insert the key-value pair 
        if slot is None:
            self.T[index] = [k,v]
            return True
        
        else:
            # if the slot is occupied, rebuild hasher and table with the new key-value pair
            keyvalues = []
            for pair in self.T:
                if pair is not None:
                    keyvalues.append(pair)
            keyvalues.append([k,v])

            oload = self.oload
            load = self.load
            self.__init__(keyvalues, oload, load)
            return True


    
# For testing: Loading in a word list

def removeNewline(s):
    if (s[-1] == '\n'):
        return s[:-1]
    else:
        return s

def wordlist(filename):
    reader = open(filename,'r')
    words = [removeNewline(line) for line in reader]
    reader.close()
    return words


# Example:

# keys = wordlist('enable.txt')


## End of file
