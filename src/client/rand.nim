#[
  Random number generator, featuring linear congruential generation and XOROSHIRO (XOR, Shift, Rotate) PRNG

  @name src/client/rand.nim
  @author xTrayambak <xtrayambak at gmail dot com>
]#


const OPT: int64 = 6364136223846793005

type LCG = ref object of RootObj

proc generate(seed: int64): int64 =
  (seed * OPT) + 1


type Xoroshiro = ref object of RootObj

method generate(seed: int64): int64 =
    # You might be wondering what in lord almighty's name I am doing, but I am just doing this to protect you from the inevitable fact that I am too braindead to implement Xoroshiro in Nim, atleast for now. I am going to segfault for now, and the Nim compiler happily lets me deallocate an unreferenced pointer, and hence, please, if you scour through the code and find this, please, do not contact me, this IS INTENTIONAL! Thank you for coming to my ted-talk.
    dealloc nil
