import React, { useState, useEffect } from "react";
import Header from "../components/Header";
import DashBoardIcon from "../assets/dashboard.png";
import ChatBot from "../components/ChatBot";
import { get } from "../services/api"; // Import the get function

const DashboardPage = () => {
  const [upcomingEvents, setUpcomingEvents] = useState([]);
  const [loadingEvents, setLoadingEvents] = useState(true);
  const [errorEvents, setErrorEvents] = useState(null);

  const [openTickets, setOpenTickets] = useState([]);
  const [loadingTickets, setLoadingTickets] = useState(true);
  const [errorTickets, setErrorTickets] = useState(null);

  const [dailyDigest, setDailyDigest] = useState("");
  const [loadingDigest, setLoadingDigest] = useState(true);
  const [errorDigest, setErrorDigest] = useState(null);

  // Knowledge base upload state removed (moved to dedicated page)

  useEffect(() => {
    const fetchUpcomingEvents = async () => {
      try {
        setLoadingEvents(true);
        const data = await get("/upcoming_events");
        if (data.events) {
          setUpcomingEvents(data.events);
        } else if (data.message) {
          setErrorEvents(data.message); // Handle cases like "No upcoming events found." or error messages
        }
      } catch (error) {
        console.error("Error fetching upcoming events:", error);
        setErrorEvents("Failed to load upcoming events.");
      } finally {
        setLoadingEvents(false);
      }
    };

    const fetchOpenTickets = async () => {
      try {
        setLoadingTickets(true);
        const data = await get("/dashboard/tickets/open");
        setOpenTickets(data);
      } catch (error) {
        console.error("Error fetching open tickets:", error);
        setErrorTickets("Failed to load open tickets.");
      } finally {
        setLoadingTickets(false);
      }
    };

    const fetchDailyDigest = async () => {
      try {
        setLoadingDigest(true);
        const data = await get("/dashboard/daily_digest");
        setDailyDigest(data.summarise_digest); // Assuming the response key is 'summarise_digest'
      } catch (error) {
        console.error("Error fetching daily digest:", error);
        setErrorDigest("Failed to load daily digest.");
      } finally {
        setLoadingDigest(false);
      }
    };

    fetchUpcomingEvents();
    fetchOpenTickets();
    fetchDailyDigest();
  }, []); // Empty dependency array means these effects run once on mount

  // handleKnowledgeBaseSubmit removed (moved to KnowledgeBaseUpload page)

  return (
    <div>
      <div className="rounded-lg py-4">
        <div className="flex items-center mb-2">
          <h1 className="text-xl mr-2">Dashboard</h1>
          <img src={DashBoardIcon} className="w-5 h-5" alt="Dashboard Icon" />
        </div>

        <div className="border border-black px-4 py-2 rounded-lg">
          <p>Daily Digest</p>
          <hr className="border-t border-gray-500 mt-2"></hr>
          <div className="grid grid-cols-1 grid-rows-3 gap-4">
            <div>
              <div className="mt-2">Upcoming Events</div>
              {loadingEvents && <p>Loading upcoming events...</p>}
              {errorEvents && <p className="text-red-500">{errorEvents}</p>}
              {!loadingEvents && !errorEvents && upcomingEvents.length === 0 && (
                <p>No upcoming events found.</p>
              )}
              {!loadingEvents && !errorEvents && upcomingEvents.length > 0 && (
                <ul>
                  {upcomingEvents.map((event) => (
                    <li key={event.id}>
                      <strong>{event.summary}</strong>:{" "}
                      {new Date(event.start.dateTime || event.start.date).toLocaleString()} -{" "}
                      {new Date(event.end.dateTime || event.end.date).toLocaleString()}
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div>
              <div className="mt-4">Tickets</div>
              {loadingTickets && <p>Loading tickets...</p>}
              {errorTickets && <p className="text-red-500">{errorTickets}</p>}
              {!loadingTickets && !errorTickets && openTickets.length === 0 && (
                <p>No open tickets found.</p>
              )}
              {!loadingTickets && !errorTickets && openTickets.length > 0 && (
                <ul>
                  {openTickets.map((ticket) => (
                    <li key={ticket.id}>
                      <strong>{ticket.issue}</strong> (Priority: {ticket.priority}, Status: {ticket.status})
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div>
              <div className="mt-4">Insights</div>
              {loadingDigest && <p>Loading insights...</p>}
              {errorDigest && <p className="text-red-500">{errorDigest}</p>}
              {!loadingDigest && !errorDigest && !dailyDigest && (
                <p>No insights available.</p>
              )}
              {!loadingDigest && !errorDigest && dailyDigest && (
                <p>{dailyDigest}</p>
              )}
            </div>
          </div>
        </div>

  {/* Knowledge Base Upload moved to its own page (/knowledge-base-upload) */}
      </div>
      <ChatBot/>
    </div>
  );
};

export default DashboardPage;



// @router.get("/dashboard/tickets/open", response_model=List[Dict])


// @router.get("/dashboard/customers/summaries", response_model=List[Dict])


// @router.get("/dashboard/daily_digest")


// @router.get("/upcoming_events")
