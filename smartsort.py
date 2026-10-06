w
# File:    smartsort.py
# Author:  John Longley
# Date:    October 2025

# Template file for Inf2-IADS (2025-26) Coursework 1, Part A:
# Implementation of hybrid Merge Sort / Insert Sort,
# with optimization for already sorted segments.


import peekqueue
from peekqueue import PeekQueue

# Global variables

comp = lambda x,y: x<=y       # comparison function used for sorting

insertSortThreshold = 10

sortedRunThreshold = 10


# TODO: Task 1. Hybrid Merge/Insert Sort

# In-place Insert Sort on A[m],...,A[n-1]:

def insertSort(A,m,n):
    """In-place Insert Sort on A[m],..,A[n-1]"""

    if n<=m:        #if n<=m do nothing
        return
    
    for i in range(m+1, n):
        x = A[i]
        j = i-1
        while j>=m and not(comp(A[j], x)):
            A[j+1] = A[j]
            j = j-1
        A[j+1] = x



def merge(C,D,m,p,n):
    """Merge C[m],...,C[p-1] and C[p],...,C[n-1] into D[m],...,D[n-1]"""

    i=m
    j=p
    k=m
    while (i<p) and (j<n):
        if comp(C[i], C[j]):
            D[k] = C[i]
            i = i+1
        else:
            D[k] = C[j]
            j = j+1
        k = k+1

    # fill in remaining elements
    while i<p:
        D[k] = C[i]
        i = i+1
        k = k+1

    while j<n:
        D[k] = C[j]
        j = j+1
        k = k+1


def greenMergeSort(A,B,m,n):
    """Merge Sort A[m],...,A[n-1] using just B[m],...,B[n-1] as workspace.
    Deferr to Insert Sort if length <= insertSortThreshold"""

    length = n-m
    if length <= insertSortThreshold:
        insertSort(A,m,n)
    else:
        q = (m+n)//2
        p = (m+q)//2
        r = (q+n)//2
        greenMergeSort(A,B,m,p)
        greenMergeSort(A,B,p,q)
        greenMergeSort(A,B,q,r)
        greenMergeSort(A,B,r,n)
        merge(A, B, m, p, q)
        merge(A, B, q, r, n)
        merge(B, A, m, q, n)



# Provided code:

def greenMergeSortAll(A):
    B = [None] * len(A)
    greenMergeSort(A,B,0,len(A))
    return A


# TODO: Task 2. Detecting already sorted runs.

def allSortedRuns(A):
    """Build and return queue of sorted runs of length >= sortedRunThreshold.
    Queue items should be pairs (i,j) such that A[i],...,A[j-1] is sorted."""

    Q = PeekQueue()
    run_start = 0
    n = len(A)

    # traverse through the array to find sorted runs
    while run_start<n:
        run_end = run_start + 1

        while run_end<n and comp(A[run_end-1], A[run_end]):
            run_end += 1
        
        # if the run is long enough, record it
        if (run_end-1) >= sortedRunThreshold:
            Q.push(run_start,run_end)
        
        # move to start of the next run
        run_start = run_end
    
    return Q



def isWithinRun(Q,i,j):
    """Test whether A[i],...,A[j-1] is sorted according to info in Q."""

    # discard any pairs in Q where run_end<=i
    while Q.peek() != None and Q.peek()[1]<=i:
        Q.pop()
    
    # check if (i,j) is within the current pair in Q 
    if Q.peek() != None:
        run_start = Q.peek()[0]
        run_end = Q.peek()[1]
        if (run_start <= i) and (j <= run_end):
            return True
    
    return False


def smartMergeSort(A,B,Q,m,n):
    """Improvement on greenMergeSort taking advantage of sorted runs."""

    # if length is small enough, use Insert Sort
    length = n-m
    if length <= insertSortThreshold:
        insertSort(A,m,n)
        return
    
    # if this is already sorted, do nothing
    if isWithinRun(Q, m, n):
        return
    
    # split the array and sort each half
    mid = (m+n)//2
    smartMergeSort(A, B, Q, m, mid)
    smartMergeSort(A, B, Q, mid, n)

    # merge the two sorted halves
    merge(A, B, m, mid, n)
    


# Provided code:

def smartMergeSortAll(A):
    B = [None] * len(A)
    Q = allSortedRuns(A)
    smartMergeSort(A,B,Q,0,len(A))
    return A


# TODO: Task 3. Asymptotic analysis of smartMergeSortAll

# 1. Justification of O(n lg n) bound.

# In the worst case, no sorted runs are found that are large enough, 
# so every recursive call has to fully process its sublist. So in this case
# smartMergeSortAll works just like greenMergeSortAll, and thus has a time 
# complexity of O(n lg n).

# The two subcalls to smartMergeSort each handles half of the list, so the 
# recursion has lg n levels since each level halves the problem size (n). 
# Merging takes Theta(n) time because each element must be checked once. 
# So the recurrence for the runtime is: T(n) = 2*T(n/2) + Theta(n)
# (a=2, b=2, k=1)
# By applying the Master Theorem, T(n) = O(n lg n)

# Building the sorted runs queue (allSortedRuns) takes O(n) time since it 
# scans through the list once. Any checks using isWithinRun during recursion
# are O(1). insertSort on sublists smaller than the insertSortThreshold (k)
# takes O(k^2) time overall, which is O(n) because k is fixed. These are all
# lower order than O(n lg n), so the overall runtime remains O(n lg n).


# 2. Runtime analysis for nearly-sorted inputs.
#
# If deleting one item makes the list sorted, allSortedRuns will find at most
# two runs whose total length is Θ(n). allSortedRuns itself takes O(n) time 
# to scan the array once. 
# During smartMergeSort, any recursive call on a sublist within one of these
# runs will be skipped by isWithinRun, so only sublists that include the 
# misplaced item need work. So the size of the subproblems halves each time,
# until the subproblem with the misplaced item has size <=insertSortThreshold,
# at which point insertSort is used.
# The merges and insertSort on the small sublists around the misplaced element
# takes at most O(lg n) total time, which is much smaller than the O(n) time
# for scanning the runs. O(n) dominates O(lg n), therefore the overall 
# asymptotic worst-case runtime of smartMergeSortAll on nearly-sorted lists
# of length n is O(n).


# Functions added for automarking purposes - please don't touch these!

def set_comp(f):
    global comp
    comp = f

def set_insertSortThreshold(n):
    global insertSortThreshold
    insertSortThreshold = n

def set_sortedRunThreshold(n):
    global sortedRunThreshold
    sortedRunThreshold = n

def set_insertSort(f):
    global insertSort
    insertSort = f


# End of file
