# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML diagram had the following classes with attributes and methods:

User class with attributes: name, email, password, and pet, plus general getters and setters.

Pet class with attributes: name, breed, and type, plus general getters and setters.

Task class with attributes: name, priority, and duration, plus general getters and setters.

In my initial design, the User class was responsible for holding user data and linking to pet information.

The Pet class was responsible for holding pet-specific data.

The Task class was responsible for holding task data and supporting updates/modifications to tasks.



**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

![alt text](image.png)

After asking Copilot to review my initial design, I realized I was missing a Scheduler/Planner class, constraints like available time per day, and task behavior methods like add, edit, remove, and list. So I updated the UML to include those pieces.

Then I asked Copilot to check for missing relationships and potential logic bottlenecks. Based on that review, I made additional updates:

1. Added a task_id to the Task class.
2. Added optional pet_name to better connect tasks to pets.
3. Enforced required-task-first scheduling.
4. Added validation for constraints (like non-negative duration and bounded priority).
5. Made the Planner explicitly connected to a specific User.
6. These changes made the design more complete and better aligned with the scheduling requirements of the project. 

![alt text](image-1.png)

![alt text](image-2.png)

![alt text](image-3.png)


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?


**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
