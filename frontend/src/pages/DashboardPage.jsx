import React, { useState, useEffect } from "react";
import DashBoardIcon from "../assets/dashboard.png";
import { get } from "../services/api"; // adjust if your API helper is elsewhere

// local spinner — no external package required
const Spinner = ({ label = "Loading..." }) => (
  <div className="flex items-center space-x-2">
    <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-gray-900" />
    <span className="text-sm text-gray-700">{label}</span>
  </div>
);

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

  useEffect(() => {
    document.title = "Kakak Agent - Dashboard";
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
          <p className="text-lg">Daily Digest</p>
          <hr className="border-t border-gray-500 mt-2"></hr>
          <div className="grid grid-cols-1 grid-rows-auto gap-4">
            <div>
              <div className="my-2 text-lg">Upcoming Events</div>
              {loadingEvents && <Spinner />}
              {errorEvents && <p className="text-red-500">{errorEvents}</p>}
              {!loadingEvents && !errorEvents && upcomingEvents.length === 0 && (
                <p>No upcoming events found.</p>
              )}
              {!loadingEvents && !errorEvents && upcomingEvents.length > 0 && (
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider"
                      >
                        Event
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider"
                      >
                        Start
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider"
                      >
                        End
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {upcomingEvents.map((event) => (
                      <tr key={event.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {event.summary}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(
                            event.start.dateTime || event.start.date
                          ).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(
                            event.end.dateTime || event.end.date
                          ).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
            <div>
              <div className="mt-4 text-lg">Tickets</div>
              {loadingTickets && <p>Loading tickets...</p>}
              {errorTickets && <p className="text-red-500">{errorTickets}</p>}
              {!loadingTickets && !errorTickets && openTickets.length === 0 && (
                <p>No open tickets found.</p>
              )}
              {!loadingTickets && !errorTickets && openTickets.length > 0 && (
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Issue
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Priority
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {openTickets.map((ticket) => (
                      <tr key={ticket.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {ticket.issue}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {ticket.priority}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {ticket.status}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>

            <div>
              <div className="mt-4 text-lg">Insights</div>
              {loadingDigest && <p>Loading insights...</p>}
              {errorDigest && <p className="text-red-500">{errorDigest}</p>}
              {!loadingDigest && !errorDigest && !dailyDigest && (
                <p>No insights available.</p>
              )}
              {!loadingDigest && !errorDigest && dailyDigest && (
                <div style={{ whiteSpace: 'pre-wrap' }}>{dailyDigest}</div>
              )}
            </div>
          </div>
        </div>

  {/* Knowledge Base Upload moved to its own page (/knowledge-base-upload) */}
      </div>
    </div>
  );
};

export default DashboardPage;



// @router.get("/dashboard/tickets/open", response_model=List[Dict])


// @router.get("/dashboard/customers/summaries", response_model=List[Dict])


// @router.get("/dashboard/daily_digest")


// @router.get("/upcoming_events")
