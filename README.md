 🌊 Blockchain-Based Blue Carbon Registry & MRV System

A backend system for registering, issuing, and transferring blue carbon credits — with on-chain auditability via an Ethereum smart contract.



 What this project does

Blue carbon credits represent carbon sequestered by coastal and marine ecosystems (mangroves, seagrasses, salt marshes). This system allows:

- Companies to register and hold carbon credit balances
- Admins to issue verified credits to registered companies
- Companies to transfer credits between each other
- Every transaction to be recorded both in a database and on-chain via a Solidity smart contract



Progress so far

**v1.0 — Flask Skeleton**
→ App factory pattern with SQLAlchemy and Flask-Login wired up
→ Base `User` model
→ Basic project structure

**v2.0 — Auth, Credits & Blockchain Foundation** *(current)*
→ User authentication — register, login, logout, session management
→ Company model linked to users with a credit balance
→ Admin-only credit issuance with full transaction records
→ Credit transfers between companies with balance validation
→ `CarbonRegistry.sol` — Solidity smart contract with on-chain balances and events
→ Environment config via `.env` for blockchain variables




 Tech Stack

- **Backend** — Flask, Flask-SQLAlchemy, Flask-Login, Flask-Bcrypt
- **Database** — SQLite
- **Blockchain** — Solidity `^0.8.0`, Web3.py, Ganache
