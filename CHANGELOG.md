# CHANGELOG


## v0.5.1 (2025-03-16)

### Bug Fixes

- Warning message for empty args ([#21](https://github.com/r-near/near-sdk-py/pull/21),
  [`ec3b7a5`](https://github.com/r-near/near-sdk-py/commit/ec3b7a5f0f9c32635bc5083d1480656381a97f4d))


## v0.5.0 (2025-03-15)

### Bug Fixes

- **ci**: New release
  ([`9decce5`](https://github.com/r-near/near-sdk-py/commit/9decce5abca63e4fb31330423a0f3c7ecbaa5707))

- **ci**: New release
  ([`e143133`](https://github.com/r-near/near-sdk-py/commit/e1431338061f12296629a85ff2befdfe87d5f411))

- **ci**: Release process
  ([`e43eeaf`](https://github.com/r-near/near-sdk-py/commit/e43eeafd05bdf54be0772e330aaf86d97d651d82))

- **near**: Add missing low-level APIs ([#17](https://github.com/r-near/near-sdk-py/pull/17),
  [`7dd01de`](https://github.com/r-near/near-sdk-py/commit/7dd01def8339ff58356bc66f96540c94c143dc6a))

### Chores

- **deps**: Create dependabot.yml
  ([`fe97dcf`](https://github.com/r-near/near-sdk-py/commit/fe97dcfafb103c6e9de5dcf9ca56daa7f8a8592e))

### Documentation

- Minor updates
  ([`78a9d7c`](https://github.com/r-near/near-sdk-py/commit/78a9d7c3fb48118435a66d5fc2ab3ba06f537718))

### Features

- Introduce Class-Based Contract Pattern ([#19](https://github.com/r-near/near-sdk-py/pull/19),
  [`275883c`](https://github.com/r-near/near-sdk-py/commit/275883c2988aa4371dd869c2bb54108858104a67))

* Improved ergonomics

* Slight changes to the README

* docs

* Update README

* clean this up

* Update docs

* Add greeting contract test

* add ownership test

* Add storage tests

- Pythonic Promise API for Cross-Contract Calls ([#5](https://github.com/r-near/near-sdk-py/pull/5),
  [`ed4b509`](https://github.com/r-near/near-sdk-py/commit/ed4b50945d6ba91f82c7aca7ac0da68d9a4379ec))

* First attempt at promises

* Parse extra args

* documentation

* Make this a private function

* Split into modules

* Apparently needs to be borsh-serialized

* Add tests for batch

* feat: Add tests CI

* Fix deps

* fix(ci): Install Python properly

* Remove this from the lint action

* Update near-pytest

* Add more tests

* Parallel tests, proper test isolation

* simplify dependencies

* Test join promises

* Test promise chain

* test promise failures

* batch promises

* batch test

* update to latest pytest

* Increase gas

* Add basic contract

* Add callback contract

* Logging

* error handling

* token gas

* account operations

* delete old contracts

* docs

* Add security check

* Linting

* Maybe no parallelization for now


## v0.4.1 (2025-03-06)

### Bug Fixes

- **ci**: Improve release process
  ([`f7fd392`](https://github.com/r-near/near-sdk-py/commit/f7fd3923102acbf3394177143de3846617269d30))


## v0.4.0 (2025-03-06)

### Chores

- **release**: 0.4.0
  ([`3913f58`](https://github.com/r-near/near-sdk-py/commit/3913f584b80662ec9f6601ab87e8a38d7b718e3b))

### Documentation

- Add more info about Collections
  ([`cecd424`](https://github.com/r-near/near-sdk-py/commit/cecd424a4e77d8088547a700ba3fcbb7260ba00c))

### Features

- Support more versions of Python ([#9](https://github.com/r-near/near-sdk-py/pull/9),
  [`169a3cd`](https://github.com/r-near/near-sdk-py/commit/169a3cd9fa4812d8cf9c7104a39215d6006c8ec2))


## v0.3.0 (2025-03-05)

### Chores

- **release**: 0.3.0
  ([`c72f1eb`](https://github.com/r-near/near-sdk-py/commit/c72f1ebb2afd8ada616e7826e1f66936d4cd5f03))

### Features

- Collections API ([#4](https://github.com/r-near/near-sdk-py/pull/4),
  [`d462bc4`](https://github.com/r-near/near-sdk-py/commit/d462bc43fed737aa3518ab2ca6f6a2c70be7fa83))

* feat: Collections API

* Strip out generics for micropython

* Switch to msgpack serialization

* Linting

* Move this to inside the SDK

* Fix imports

* Add docs

* Rename this job

* Switch to pickle (it's native)

* Use generic Exception class


## v0.2.0 (2025-03-04)

### Chores

- **release**: 0.2.0
  ([`204dbb8`](https://github.com/r-near/near-sdk-py/commit/204dbb8f468562ed8c0b7c3b1e6e8f5a223d0383))

### Documentation

- Update README
  ([`ef14f6a`](https://github.com/r-near/near-sdk-py/commit/ef14f6ab788404542320d1cda5efd58100db7e6f))

### Features

- Add Simplified Promise API with Callback Support
  ([#3](https://github.com/r-near/near-sdk-py/pull/3),
  [`fd79fbd`](https://github.com/r-near/near-sdk-py/commit/fd79fbdf50d388cb8808fa51a9ca048a8e5eacce))

* feat: Add a high-level promises API

* docs: Add info on Promises usage


## v0.1.2 (2025-03-04)

### Bug Fixes

- Add GitHub token to release workflow
  ([`863f8dc`](https://github.com/r-near/near-sdk-py/commit/863f8dcaadfa1601a84b79ba962945017a772c8a))

- Add release workflow ([#2](https://github.com/r-near/near-sdk-py/pull/2),
  [`d57b0ee`](https://github.com/r-near/near-sdk-py/commit/d57b0ee8221e647143c68f4a7b2fe8ffe4ea523b))

* fix: Add release workflow

* Fix lockfile

- Fetch tags for release
  ([`c48def0`](https://github.com/r-near/near-sdk-py/commit/c48def02011ae4aa8672dc1db15fbb04d65c017c))

- Set env variable in the correct location
  ([`0c14d1c`](https://github.com/r-near/near-sdk-py/commit/0c14d1c6a90803b52608078e85b459156685a54e))

- Update fetch-depth
  ([`409f217`](https://github.com/r-near/near-sdk-py/commit/409f217dab37d722af12e757aeea9e154add4d3c))

### Chores

- Auto-run on main
  ([`a1d3f7b`](https://github.com/r-near/near-sdk-py/commit/a1d3f7b4f389f975ed0b8ca6abf1dcd9f7dc9daa))

- Update permissions
  ([`0e9b3ae`](https://github.com/r-near/near-sdk-py/commit/0e9b3aee307aababe8db3ba2c61c7c661516f390))

- **release**: 0.1.2
  ([`9667445`](https://github.com/r-near/near-sdk-py/commit/96674452eef1cb6628c8f35d4a6ee8d6def8d8ab))


## v0.1.1 (2025-03-03)

### Bug Fixes

- Circular imports in WASM
  ([`a56b757`](https://github.com/r-near/near-sdk-py/commit/a56b75790be8d6a01ad34aac4509ec4d1383cd9e))
