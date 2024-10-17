# PDF Reader Angular

![Angular](https://img.shields.io/badge/Angular-18.2.0-red)
![TypeScript](https://img.shields.io/badge/TypeScript-5.5.2-blue)
![RxJS](https://img.shields.io/badge/RxJS-7.8.0-purple)
![Zone.js](https://img.shields.io/badge/Zone.js-0.14.10-yellowgreen)

## Description

This project is built with **Angular** (v18.2.0) and utilizes **TypeScript** and **RxJS** for a robust front-end application. It includes a variety of tools and packages like Angular Material, PDF handling libraries, and linting configurations to enhance the development process.

<p align="center">
   <img src="https://github.com/user-attachments/assets/02074ed6-dc5a-4141-a6ec-8982d3657ba9" alt="ezgif-6-c7aa0a31dc" />
</p>

### Branch Naming Rules

| Branch Name                    | Description            | Supplemental |
| ------------------------------ | ---------------------- | ------------ |
| main                           | latest release         |              |
| dev/main                       | latest for development |              |
| hotfix/{module name}/{subject} | Hotfix branch          |              |
| sandbox/{anything}             | test code, etc.        |              |

### Branch Rules

-   Work is branched from each latest branch.
-   Delete working branches after merging.
-   Review as much as possible (have someone do it for you).
-   Build, deploy, etc. are discussed separately.

## Front End Setup

This project is built using **Angular** and requires **Node.js** to run locally. Follow the steps below to install and run the project.

### Prerequisites

1. **Install NodeJS**  
   Ensure you have Node.js installed on your machine. You can download it from [nodejs.org](https://nodejs.org/en/download/).

2. **Install Angular CLI**  
   If you do not have the Angular CLI installed, you can install it globally using npm:

    ```bash
    npm install -g @angular/cli
    ```

3. **Install pnpm**  
   The project uses `pnpm` as the package manager. You can install it using the following command:

    ```bash
    npm install -g pnpm
    ```

### Installation

Once the prerequisites are installed, follow these steps to set up the project:

1. **Clone the repository**:

    ```bash
    git clone <repository-url>
    ```

2. **Navigate to the project directory**:
    ```bash
    cd frontend
    pnpm install
    ```

### Running the Application

After installing the dependencies, you can run the Angular application locally:

1. **Start the development server**:

    ```bash
    pnpm run start
    ```

    This command will start a local server, and you can access the application at [http://localhost:4200](http://localhost:4200).

## Running Backend

 ```bash
 pip install poetry
 poetry install --no-root
 poetry run python app.py
 ```

## Commit message

Please refer to the following template for the commit message.

```plaintext
🐞 Bugs and Performance
#🐛 :bug: bug fixes.
#🚑 :ambulance: fix a critical bug
#🚀 :rocket: performance improvements
#💻 Code quality and style
#👍 :+1: feature improvements
#♻️ :recycle: refactoring
#👕 :shirt: Lint error fixes and code style fixes

🎨 UI/UX and design
#✨ :sparkles: add new features
#🎨 :art: design changes only

🛠️ Development Tools and Settings.
#🚧 :construction: WIP (Work in Progress)
#⚙ :gear: config change
#📦 :package: add new dependency
#🆙 :up: update dependency packages, etc.

documentation and comments.
#📝 :memo: fix wording
#📚 :books: documentation
#💡 :bulb: add new ideas and comments

🛡️ security
#👮 :op: security-related improvements

🧪 testing and CI.
#💚 :green_heart: fix/improve testing and CI

🗂️ file and folder manipulation.
#📂 :file_folder: Folder manipulation
#🚚 :truck: file movement

#📊 :log: logging and tracking
#💢 :anger: conflicts
#🔊 :loud_sound: add log
#🔇 :mute: log deleted.
#📈 :chart_with_upwards_trend: add analytics or tracking code

💡 Other.
#🧐 :monocle_face: code reading and questions.
#🍻 :beers: code that was fun to write.
#🙈 :see_no_evil: .gitignore addition.
#🛠️ :hammer_and_wrench: bug fixes and basic problem solving
```
