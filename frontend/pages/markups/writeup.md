# COMP 4300 - TopogChamp Writeup

## Introduction
The goal of this project is to provide a interactive tool that facilitates the learning of the OSI model network layer for those who are visual learners. 
By applying networking terms and concepts taught during lectures to our project, we hoped to reinforce our learning by implementing these ideas into an open-ended application that allows the user to build and simulate their own networks.
Simplified controls such as drag-and-drop for organizing end-systems and network links make our application more accessible when compared to a tool that uses a command line or a simple GUI.
A tool with high accessibility and an easy-to-use interface can be used to effectively teach grade school students or casual learners about different networking concepts.

## Frontend: Network Node Interface
In order to provide an interactive and appealing interface for our application, we made use of the open source `vis.js` network visualization tool. 
This tool provides an easy means of organizing network nodes on a blank canvas through the use of drag-and-drop controls. 
These nodes are connected by edges. 
The user can then create or delete edges between nodes using a simple edge editor toolbar at the top left of the screen. 
`vis.js` on its own does not provide network emulation capabilities, so we had to use a different tool for such simulations.

## Backend: Network Emulation
The networking layer of the OSI model is a multifaceted ordeal. 
One must take several factors into consideration to ensure that packets are promptly delivered to the intended recipient without issues. 
These factors include, but are not limited to, network delays, packet loss and bandwidth limitations.
By using the open source tool Kathara, we may simulate these factors in a sandbox environment.
Kathara allows the user to create and run simulated devices. 
These devices may then communicate with other simulated devices. 

The node and edge structures created by the user through `vis.js` can then be converted into a network of Kathara devices before starting a simulation. 
The purpose of such a simulation would be to test the ruggedness of the user's design under adverse conditions.
We may then design simple levels that ask the user to reach certain goals such as a reaching target throughput or ensuring that a network packet reaches the proper recipient by following correct router links.

## Conclusion
By combining the interactive capabilities of `vis.js` and the emulation capabilities of Kathara, we are able to create an application that allows for an accessible means of organizing and running simulated Kathara devices.
This opens up networking concepts to those who prefer learning with a visual aid, or those who would like to design and test their own networks without much hassle or command line usage.
