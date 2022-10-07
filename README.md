# Time Tracker

![Django CI Badge](https://github.com/fxie520/Time-Tracker/actions/workflows/CI.yml/badge.svg)
![Django CD Badge](https://github.com/fxie520/Time-Tracker/actions/workflows/CD.yml/badge.svg)
![Apache 2.0 License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)

**Checkout Time Tracker [here](https://www.timetracker.club) !**

## Description

[Time Tracker](https://www.timetracker.club) is designed to keep track of one's disposable time 
(contrary to periods of time that one has no control on, like time at work or at school etc.).

It organizes a user's time as follows:
- A stage contains multiple days, while a day belongs to one single stage.
- A day contains multiple sessions, while a session belongs to one single day.
- A subject contains multiple sessions, while a session belongs to one single subject.
- A session belongs to one single day, and one single subject.

<p align="center">
<img alt="" src="https://github.com/fxie520/Time-Tracker/blob/main/time_tracker/static/Time_organization.png"/>
Organization of a user's time
</p>

Time Tracker automatically generates your per-stage, per-subject & per-day statistics, 
which can be used to extract meaningful insights, promote self-awareness and work efficiency.

## Example of usage

Tom, undergrad student, wakes up and start the first day of his Fall 2022 semester. 
He creates a new stage "Fall 22", a new day "09/01/2022" belongs to it, and a new subject "Algorithms" for a course he takes this semester. Since the day ("09/01/2022") is yet ended, for now he leaves "worktime", "end time", "end after midnight" and "comment" fields as default.

Tom leaves for school, finishes his lectures, goes back to the dorm, and starts working on a problem set for the algorithms course.
He creates a session which belongs to the day "09/01/2022" and the subject "Algorithms". 
Since the session is not yet ended, he leaves "end time" and "end after midnight" fields as default for now.
After some time, he stops working to have his dinner. 
He finds his latest session on "My sessions" page, clicks update, and specifies the "end time" and "end after midnight" fields.
This procedure is repeated for a few other sessions. 

Before going to bed, Tom finds the day "09/01/2022" on "My days" page, ends it by specifying relevant fields.
