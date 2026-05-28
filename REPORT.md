# Project Report

#### The Team members

* Names, epita email addresses, and GitHub usernames of all team members.

---

Abdullah Salman , Abdullah.salman@epita.fr , AbdullahSalman1

Divine Byishimo , divine.byishimo@epita.fr, divine-collab

Muhammad Saim Chaudhary , muhammad-saim.chaudhary@epita.fr , saimaziz1214


#### Initial Design

* initial architecture
* assumptions
* technical choices

When we first approached this project, we did not immediately jump into coding. We started by trying to understand what the system actually needed to do at its core. After reading the project brief carefully, we identified that the fundamental purpose was:  **receive documents, read them, extract useful content, store it, and then let users interact with it through AI** .

our initial architecture was

User uploads file
      ↓
System detects file type
      ↓
Correct reader processes the file
      ↓
Extracted content saved to database
      ↓
User queries the content via AI
      ↓
AI returns answer


---

#### Engineering Decisions

For each major decision:

* what alternatives were considered?
* why was this solution chosen?We decided early on to build this as a  **backend-first system** , meaning we would implement and test each component independently before connecting them together. This decision came from a practical concern: if we tried to build everything at once, we would not know where bugs were coming from.We also decided to keep the architecture  **modular from the start** . Each component (file readers, database, search, AI query) would be a separate Python module with a clear, single responsibility. This made it easier to divide work among team members and to test each piece independently.

#### Who Did What?

* Document how the project was originally divided among each team member.
* Document how responsibilities possibly evolved over time.

Divine: worked on the base by implementing file readers and Gemini AI query

Abdullah: worked on sql , fronted and prompt engineering

Saim: worked on cost observability and connecting flask

---

#### AI Collaboration

Document how AI tools were used.

* What tools were used for what purposes?
* How did AI influence design and implementation decisions?
* How did AI impact your learning and development process?
* How did you evaluate AI-generated suggestions?
* How did you detect and handle AI errors or limitations?

Mainly we used claude 

AI helped us so much in making decisions mainly it was directing us not straight but asking us question until we could get that maybe the decision we wanted to take wasn't perfect 

AI explained everything step by step and it could not implement the code until you ask it to help so we learnt alot

Sometimes suggestions we not direct or were a bit confusing because this project was a bit huge but we could still ask AI to explain more

We basicly asked alot of questions until it figures its confussion

---

#### Failures and Iterations

Document:

* what failed?
* what surprised you?
* what required redesign?

Sometimes AI could implement the code and if you use another agent we could see some bugs it did not happen a lot of times but it was so frustrating sometimes we could even the same agent to study the code bu tstill it finds its own mistakes

---

#### “When AI Failed or Was Wrong”

Document cases where AI-generated advice, code, or explanations were:

* incomplete
* misleading
* incorrect
* inefficient

Explain how you detected the issue and how you resolved it.

For this somrtimes one of us could push when he/she thinks it is complete but another one to continue from others work we could notice incomplete code or nonrelated codes

---

#### Lessons Learned

Reflect on:

* technical growth
* workflow improvements
* Strengths and limitations of AI-assisted development.  we learnt alot of new things from this project and we learnt new things on how using AI correctly. It is so sad that we did not have so much time to work on this project but still we learnt a lot. We did not
