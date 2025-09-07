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
      <div className="rounded-lg spacing-responsive">
        <div className="flex items-center mb-4">
          <h1 className="text-responsive-xl mr-2">Dashboard</h1>
          <img src={DashBoardIcon} className="w-5 h-5 md:w-6 md:h-6" alt="Dashboard Icon" />
        </div>

        <div className="border border-black px-2 py-4 md:px-4 md:py-6 rounded-lg">
          <p className="text-responsive-lg">Daily Digest</p>
          <hr className="border-t border-gray-500 mt-2 mb-4"></hr>
          <div className="space-y-6 md:space-y-8">
            <div>
              <div className="mb-4 text-responsive-base font-semibold">Upcoming Events</div>
              {loadingEvents && <Spinner />}
              {errorEvents && <p className="text-red-500 text-responsive-sm">{errorEvents}</p>}
              {!loadingEvents && !errorEvents && upcomingEvents.length === 0 && (
                <p className="text-responsive-sm">No upcoming events found.</p>
              )}
              {!loadingEvents && !errorEvents && upcomingEvents.length > 0 && (
                <div className="table-responsive">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th
                          scope="col"
                          className="px-2 md:px-6 py-3 text-left text-xs font-medium uppercase tracking-wider"
                        >
                          Event
                        </th>
                        <th
                          scope="col"
                          className="px-2 md:px-6 py-3 text-left text-xs font-medium uppercase tracking-wider"
                        >
                          Start
                        </th>
                        <th
                          scope="col"
                          className="px-2 md:px-6 py-3 text-left text-xs font-medium uppercase tracking-wider hidden sm:table-cell"
                        >
                          End
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {upcomingEvents.map((event) => (
                        <tr key={event.id}>
                          <td className="px-2 md:px-6 py-4 text-responsive-xs font-medium text-gray-900">
                            <div className="break-words">{event.summary}</div>
                          </td>
                          <td className="px-2 md:px-6 py-4 text-responsive-xs text-gray-500">
                            <div className="break-words">
                              {new Date(
                                event.start.dateTime || event.start.date
                              ).toLocaleString()}
                            </div>
                          </td>
                          <td className="px-2 md:px-6 py-4 text-responsive-xs text-gray-500 hidden sm:table-cell">
                            <div className="break-words">
                              {new Date(
                                event.end.dateTime || event.end.date
                              ).toLocaleString()}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
            
            <div>
              <div className="mb-4 text-responsive-base font-semibold">Tickets</div>
              {loadingTickets && <p className="text-responsive-sm">Loading tickets...</p>}
              {errorTickets && <p className="text-red-500 text-responsive-sm">{errorTickets}</p>}
              {!loadingTickets && !errorTickets && openTickets.length === 0 && (
                <p className="text-responsive-sm">No open tickets found.</p>
              )}
              {!loadingTickets && !errorTickets && openTickets.length > 0 && (
                <div className="table-responsive">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th
                          scope="col"
                          className="px-2 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                          Issue
                        </th>
                        <th
                          scope="col"
                          className="px-2 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                          Priority
                        </th>
                        <th
                          scope="col"
                          className="px-2 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden sm:table-cell"
                        >
                          Status
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {openTickets.map((ticket) => (
                        <tr key={ticket.id}>
                          <td className="px-2 md:px-6 py-4 text-responsive-xs font-medium text-gray-900">
                            <div className="break-words">{ticket.issue}</div>
                          </td>
                          <td className="px-2 md:px-6 py-4 text-responsive-xs text-gray-500">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              ticket.priority === 'High' ? 'bg-red-100 text-red-800' :
                              ticket.priority === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-green-100 text-green-800'
                            }`}>
                              {ticket.priority}
                            </span>
                          </td>
                          <td className="px-2 md:px-6 py-4 text-responsive-xs text-gray-500 hidden sm:table-cell">
                            <div className="break-words">{ticket.status}</div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            <div>
              <div className="mb-4 text-responsive-base font-semibold">Insights</div>
              {loadingDigest && <p className="text-responsive-sm">Loading insights...</p>}
              {errorDigest && <p className="text-red-500 text-responsive-sm">{errorDigest}</p>}
              {!loadingDigest && !errorDigest && !dailyDigest && (
                <p className="text-responsive-sm">No insights available.</p>
              )}
              {!loadingDigest && !errorDigest && dailyDigest && (
                <div 
                  className="text-responsive-sm bg-gray-50 p-3 md:p-4 rounded-md border border-gray-200"
                  style={{ whiteSpace: 'pre-wrap' }}
                >
                  {dailyDigest}
                </div>
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
