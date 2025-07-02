# QuakerCMS

[![CI](https://github.com/WesternFriend/QuakerCMS/workflows/CI/badge.svg)](https://github.com/WesternFriend/QuakerCMS/actions)
[![codecov](https://codecov.io/gh/WesternFriend/QuakerCMS/branch/main/graph/badge.svg)](https://codecov.io/gh/WesternFriend/QuakerCMS)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Django 5.2+](https://img.shields.io/badge/django-5.2+-green.svg)](https://djangoproject.com/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

A specialized content management system designed for Quaker meetings and worship groups to publish and share their spiritual writings, announcements, and community content.

## Purpose

QuakerCMS provides a standardized platform for Quaker communities to publish and discover important content, fostering connection and continuity within the broader Quaker movement. The system recognizes the unique content types and communication patterns that are central to Quaker spiritual life and community organization.

## Vision

We envision a federated network of Quaker websites that can share content with one another, making it easier for meetings and worship groups to:

- Preserve and share their spiritual writings and corporate decisions
- Discover content from other Quaker communities
- Maintain their historical records in a structured, accessible format
- Connect with the broader Quaker movement through shared resources

## Key Features

### Content Types for Quaker Communities

QuakerCMS is designed to handle the specific types of content that Quaker communities regularly publish:

- **Epistles** - Formal spiritual letters and communications between meetings, part of the rich tradition of Quaker writings
- **Minutes** - Records of business meetings and corporate decisions
- **Announcements** - Community news and updates
- **Events** - Structured event information with relevant details (time, location, description)
- **Newsletters** - Regular community publications
- **Pamphlets** - Educational and spiritual materials

### Technical Goals

- **Multi-tenant Architecture** - Single instance can host multiple meetings and worship groups
- **Content Federation** - Meetings can share content with other instances for broader discovery
- **Multi-lingual Support** - Internationalization and localization capabilities for global Quaker communities
- **Standards-Based** - Uses open web standards for content syndication (RSS, Atom)
- **Mobile-Friendly** - Responsive design that works on all devices
- **Open Source** - No dependency on proprietary services or software
- **Simple Management** - Easy-to-use interface for content managers

## Use Cases

### Individual Meetings
- Publish weekly announcements and newsletters
- Share minutes from business meetings
- Maintain event calendars
- Create digital archives of important documents

### Regional Bodies
- Aggregate epistles and minutes from constituent meetings
- Coordinate regional events and communications
- Maintain directories of meetings and worship groups

### Broader Quaker Community
- Discover spiritual writings and epistles from meetings worldwide
- Research historical documents and decisions
- Stay connected with the global Quaker movement

## Stakeholders

### Primary Users
- **Meeting Clerks** - Responsible for publishing official meeting communications
- **Content Managers** - Members designated to maintain website content
- **Newsletter Editors** - Those who compile and publish regular communications

### Administrative Roles
- **Technical Coordinators** - Manage site infrastructure and custom domains
- **Site Administrators** - Configure initial site settings and user permissions

### Community Members
- **Meeting Attenders** - Access community content and internal resources
- **Researchers** - Scholars and historians studying Quaker writings and decisions
- **Other Meetings** - Discover and learn from content published by peer communities

## Getting Started

For information on setting up a development environment or contributing to the project, see our [Contributing Guide](CONTRIBUTING.md).

## Technology Stack

QuakerCMS is built with:
- **Python 3.12+** - Modern Python for reliable backend development
- **Django** - Robust web framework for rapid development
- **Wagtail CMS** - Flexible content management system with excellent editing experience
- **uv** - Fast Python package management

## Project Status

QuakerCMS is in active development. We are working toward an initial release that will support basic content management for individual meetings, with federation and multi-tenant capabilities planned for future releases.

## Community

This project is developed collaboratively by members of the Quaker community who understand the unique needs of our spiritual tradition. We welcome contributions from both technical and non-technical community members.

## License

QuakerCMS is licensed under the AGPL-3.0-or-later license, ensuring it remains free and open source for the Quaker community.
