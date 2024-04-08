# COMP 4300 - TopogChamp Writeup

## Project Idea

The goal of this project is to provide an interactive tool that facilitates the learning of the OSI model network layer for those who are visual learners. By applying networking terms and concepts taught during lectures to our project, we hoped to reinforce our learning by implementing these ideas into an open-ended application that allows the user to build and view their own networks. Simplified controls such as drag-and-drop for end-system and network link organisation makes our application more accessible when compared to a tool that uses a command line or a simple GUI. Such a tool with high accessibility and an easy-to-use interface can be used to effectively teach grade school students or casual learners about different networking concepts.

By implementing the “vis.js” library for Javascript, we may render a two-dimensional graph that allows for node and edge editing. The graph structures created by the user can be tested by the game to invoke the user’s learning of these simple network topologies. This allows the user to interact with the way topologies are made from the set of end systems, links, routers, and nodes. This gives the user a bird’s eye view to provide a different perspective on the formation of these network topologies.

## Technical Components

### Network Node Graphical User Interface

In order to provide an interactive and appealing interface for our application, we made use of the open source “vis.js” network visualization tool. This tool provides an easy means of organizing network nodes on a blank canvas through the use of drag-and-drop controls. These nodes are connected by edges. The user can then create or delete edges between nodes using a simple edge editor toolbar at the top left of the screen. “vis.js” on its own does not provide network emulation capabilities, so we had to use another tool for such simulations.

### Network Emulation

The networking layer of the OSI model is a multifaceted ordeal. One must take several factors into consideration to ensure that packets are promptly delivered to the intended recipient without issues. These factors include, but are not limited to, network delays, packet loss and bandwidth limitations. By using the open source tool Kathara, we may simulate these factors in a sandbox environment. Kathara allows the user to create and run simulated devices, with additional options for simulating adverse network conditions as mentioned above. Devices created in Kathara may then communicate with other simulated devices. In our project, we have implemented this by using Kathara for recreating the server network structure at the University of Manitoba.

## Project Outcomes

By combining the interactive capabilities of “vis.js” and the emulation capabilities of Kathara, we are able to create an application that allows for an accessible means of organising and running simulated Kathara devices. This opens up networking concepts to those who prefer learning with a visual aid, or those who would like to design and test their own networks without much hassle or command line usage.

## Game Aspect

This graphical interactive interface has potential for gamification. It is possible to design simple levels that ask the user to achieve certain goals such as a reaching target throughput or ensuring that a network packet reaches the proper recipient by following correct router links.

In our application, we have implemented a preliminary version of such a game. The user is tasked with recreating different network topologies using the drag and drop features. Once the network in question is created, the user may submit their answer. An internal check is performed before outputting a “Success” or “Failure”. We had hoped to implement levels that include advanced requirements such as bandwidth targets and correct package routing through header tables. The simulation capabilities of Kathara will allow for user-created networks to be tested under adverse conditions such as packet loss and bandwidth delays. The gamification aspect of this tool has potential to be explored further.

## Simulation

The simulation component of our software was created to provide clients with an opportunity to see details of the current network. And, eventually, use it for auto-creating new scenarios for the game to avoid spending time coming up with real-world scenarios of companies’ networks.

Since creating end-to-end software of such kind was not feasible it was decided to cover one of the scenarios to showcase possibilities of potential end product. Hence, when the simulation runs it scans a small part of the U of M network. In particular, the client scans the /28 subnet to the right of its Authoritative DNS server. After that, the Tacata script was modified and used to support Kathara 2.0 for the specific use case. Our Tacata script generates a Kathara lab Networking lab that serves as part of the backend for the simulation. Then NetVis tool is used for visualization of the created lab so that the client can see the graph of the network.

## Challenges

The challenges faced in the project were plentiful. From the shell script for ease of startup to the marking of the user inputted topologies in the game, we found ourselves with our fair share of opportunities to learn. The shell script had challenges stemming from the various operating systems we utilize in normal day to day usage. We had to fix the project to Windows due to the value provided from the `ipconfig` command, which is not found on Unix systems. This command allowed us to generate the needed information to develop the simulation of a section of the user’s network's current DNS server topology. Additionally, the usage of `net-vis-localhost` exists as a Windows executable. We attempted to implement Linux and MacOS versions of this program, but we failed in that aspect unfortunately. Overall, the shell script we created had a goal of making the (Windows) user have an easy time to set up the project and allow the user to start playing/learning quickly. This challenge was well worth it, because the usage of the shell script `run.sh` effectively runs the project.

Another challenge faced was the development of the game. Initially we attempted to use a library called `Phaser.js` to create our game logic. We found this library to be confusingly documented and did not work for the game we were trying to implement. Using `Phaser.js`, we developed a simple game with the connection of nodes via wires, but the performance was abysmal. As a group, we found the code to be confusing, often finding ourselves lost in the many objects created to just make a simple UI. We then found `vis.js` which is a library that displays networks. This then alleviated the challenge of a frontend library to handle user interaction.

We have also faced a challenge when trying to simulate the U of M network. Scanning the entire network would take too long and require too many requests which could have created issues for the University network, and therefore not a good idea. Hence, it was decided to just scan /28 subnet to the right of the client DNS server to get network components for generating our demo graph. But the software is meant to be used; it is permitted by the network administrators to do a deep scan of the entire network to avoid manually typing in information for generating network graphs.

## Evaluation

In totality, the project was achieved with a visually appealing interface, intuitive controls, and a graphical structure that is a correct representation of a Kathara generated network. We believe the look and feel of the front-end is visually appealing and nice to use. Its simplicity and colour scheme allow the user to focus on the key developments from the project, like the game and simulation. The controls for the game allow the user to effectively manipulate the nodes and edges within the network to make the needed network topologies. Using the keyboard and mouse in combination allow the user to effectively change the network to their liking. Additionally, the graphical structure of the generated network that is emulated from Kathara has multiple virtual machines that use the data obtained from the `getNetworkData.py` script. This simulated network is then hosted locally and piped into our main project. This allows the user to, similarly to the game, manipulate and navigate the network they are connected to. This functions only on the UManitoba network because we need a network infrastructure that we have permission to scan.

Through a small experiment, we consulted participants that are not well versed in network topologies. The few participants stated that they found the UI to be appealing. As well, when playing the game, they did not understand what to create initially, but after learning a little about topologies, they followed their intuition and created connections necessary to correctly connect the nodes in the systems to complete a few levels. The “Bus” network was overall a challenge due to its greater complexity over the other levels. They used the game interface effectively and smoothly. Additionally, they explored the simulation of the network they were connected to and asked questions like, “This is what my computer is connected to right now?”. With these factors, we believe that the project successfully taught others a surface level of network topologies and stimulated some learning in the participants. Of our sample of 3 participants, the consensus was that the goals were achieved.

## Improvements

We did not delve deeply into the gamification aspect of our application. It would have been ideal to add more game levels that feature advanced challenges. As previously mentioned, the user could have been tasked with reaching a bandwidth threshold by routing packets through network links with packet loss. Another feature that could have been added is a header table interface. It would have allowed the user to edit the header tables of routers in order to direct the flow of packet traffic.

Another improvement would be to implement Kathara Labs as a backend. Kathara labs allows for the creation of a Kathara simulation from an existing network. We may then insert this emulated network into our application automatically. In combination with the advanced game features mentioned above, we can then run tests on the emulated network to test its capabilities during less-than-ideal conditions such as heavy traffic, high packet loss and packet delays.
