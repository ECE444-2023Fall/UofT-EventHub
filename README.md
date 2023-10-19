[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-718a45dd9cf7e7f842a935f5ebbe5719a5e09af4491e668f4dbf3b35d5cca122.svg)](https://classroom.github.com/online_ide?assignment_repo_id=11975958&assignment_repo_type=AssignmentRepo)

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
![GitHub contributors](https://img.shields.io/github/contributors/ECE444-2023Fall/project-1-web-application-design-group9-netninjas)

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

The goal of the project is to create a user-centric event management platform that enhances the
experience of students, faculty, and staff at the University of Toronto (UofT) by providing an accurate
and user-friendly solution for discovering, managing, and participating in events and activities. Our
platform aims to serve as a one stop solution which significantly reduces the time and effort required
to stay informed and engaged for students, clubs, and faculty members at the University of Toronto.

<!-- GETTING STARTED -->
## Getting Started

We have dockerized the project to prevent any complications that might arise from different environments. TO run the application locally you can:

- Initialize the python docker image using the Dockerfile we have added
```docker build -t python-docker .```

- Run the website locally on a specific port
```docker run -d -p 5000:5000 python-docker```

<!-- ROADMAP -->
## Roadmap

This is a near-term roadmap for the tasks that are priorotized by the team. A more detailed issue management information can be found on our GitHub Project management tool [here](https://github.com/orgs/ECE444-2023Fall/projects/4).

- [x] Define the database schemas 

- [x] Define database integrity constraints

- [x] Make login/register page

- [x] Make blank user entry page

- [x] Make blank organizer entry page

- [x] Make successful redirection for users/organizers

- [x] Make a credentials database and connect it with the website

- [x] Add functionality to register users

- [x] Add functionality to register organizers

- [x] Make a sample events database – 3-4 entries

- [ ] Show all users the same event feed from the events database

- [ ] Add functionality for organizers to add an event to the database

- [ ] Organize events in a list view for users

- [ ] Organize events in a calendar view for users

- [ ] Add sorting of events for users

- [ ] Import events to Google calendar

- [ ] Add ratings for organizer’s

- [ ] Add ability for users to add ratings

- [ ] Add functionality to assign tags to events (for organizers)

- [ ] Add search for events (user side)

- [ ] Add functionality to help users define and store their preference

See the [open issues](https://github.com/ECE444-2023Fall/project-1-web-application-design-group9-netninjas/issues?q=is%3Aopen+is%3Aissue) for a full list of proposed features (and known issues).

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please set the reviewers of your pull requests to either @pandyah5 or @snehshah09

<!-- CONTACT -->
## Contact
The best way to contact us is to join our [discord server] (https://discord.gg/8smuwBk4)

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

We would like to acknowledge the ECE444 Teaching Team from the University of Toronto, who has guided us all the way to build this project.