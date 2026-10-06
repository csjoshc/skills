# Parcel Pal: rough requirements

Fictional internal tool for the Harbor Lane warehouse team.

## Goal
Give dock staff one screen that shows today's inbound parcels and flags
late ones, so they stop checking three carrier websites.

## What we want
- Pull tracking status for inbound parcels from the carriers we use
- Show a list sorted by expected arrival, late ones highlighted red
- Dock staff can mark a parcel "received" with one tap
- Send a Slack message to #dock when a parcel is more than 4 hours late

## Approach (already decided)
- Split into five microservices (ingest, status, notify, auth, gateway)
  deployed on Kubernetes
- Use Kafka between the services
- React front end

## Notes
- About 40 parcels a day today
- Team is two developers and no dedicated ops person
- Want a first version in three weeks
- Carrier tracking data will be available through their APIs
