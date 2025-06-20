# Geotagging App

## Overview
The Geotagging App is a Python application that allows users to geotag personal, cultural, or historical stories onto a map. Users can add text, images, audio, and video to create a crowdsourced memory layer over real-world locations. The app enables exploration via map, filters, and a timeline.

## Features
- User authentication with signup and login functionality.
- Ability to geotag stories with multimedia content.
- Interactive map interface for exploring geotagged content.
- Filtering options to refine story searches.
- Timeline view for chronological exploration of stories.

## Project Structure
```
geotagging-app
├── src
│   ├── main.py            # Entry point of the application
│   ├── auth.py            # User authentication module
│   ├── map_interface.py    # Map interface management
│   ├── utils.py           # Utility functions
│   └── data
│       └── user.json      # User information storage
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```

## Setup Instructions
1. Clone the repository:
   ```
   git clone <repository-url>
   cd geotagging-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python src/main.py
   ```

## Usage Guidelines
- Upon launching the application, users will be prompted to either sign up or log in.
- After authentication, users can access the map interface to geotag their stories.
- Users can explore existing stories using the map and apply filters to find specific content.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License.