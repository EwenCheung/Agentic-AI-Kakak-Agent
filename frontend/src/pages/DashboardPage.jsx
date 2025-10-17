import React, { useState, useEffect } from "react";
import DashBoardIcon from "../assets/dashboard.png";
import { get, toggleTicketStatus, deleteTicket, getAllTickets } from "../services/api"; // adjust if your API helper is elsewhere
import { DeleteIcon, CheckIcon } from "../components/Icons";
import Toast from "../components/Toast";
import useSuccessNotification from "../hooks/useSuccessNotification";

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

  const [openTickets, setOpenTickets] = useState([]);
  const [loadingTickets, setLoadingTickets] = useState(true);
  const [errorTickets, setErrorTickets] = useState(null);
  const [processingTickets, setProcessingTickets] = useState(new Set()); // Track which tickets are being processed

  const [dailyDigest, setDailyDigest] = useState("");
  const [loadingDigest, setLoadingDigest] = useState(true);
  const [errorDigest, setErrorDigest] = useState(null);

  // Toast notification state and hook
  const [toast, setToast] = useState({ show: false, type: '', title: '', message: '' });
  const { showSuccess, showError } = useSuccessNotification(setToast);

  const fetchDailyDigest = async (events = [], tickets = []) => {
    try {
      setLoadingDigest(true);
      
      // Check if both events and tickets are empty
      if (events.length === 0 && tickets.length === 0) {
        setDailyDigest("No data is found today. You can go to the configuration page to configure your own AI if you haven't set up an account.");
        return;
      }
      
      const data = await get("/dashboard/daily_digest");
      setDailyDigest(data.summarise_digest); // Assuming the response key is 'summarise_digest'
    } catch (error) {
      console.error("Error fetching daily digest:", error);
      setErrorDigest("Failed to load daily digest.");
    } finally {
      setLoadingDigest(false);
    }
  };

    const fetchOpenTickets = async () => {
      try {
        setLoadingTickets(true);
        const data = await getAllTickets(); // Get all tickets instead of just open ones
        setOpenTickets(data);
      } catch (error) {
        console.error("Error fetching tickets:", error);
        setErrorTickets("Failed to load tickets.");
      } finally {
        setLoadingTickets(false);
      }
    };  const handleToggleTicketStatus = async (ticketId) => {
    setProcessingTickets(prev => new Set([...prev, ticketId]));
    try {
      const response = await toggleTicketStatus(ticketId);
      // Refresh the tickets list to show updated status
      await fetchOpenTickets();
      
      // Show success message based on the action
      if (response.new_status === 'closed') {
        showSuccess('Ticket closed successfully!');
      } else {
        showSuccess('Ticket reopened successfully!');
      }
    } catch (error) {
      console.error("Error toggling ticket status:", error);
      setErrorTickets("Failed to toggle ticket status.");
      showError("Failed to toggle ticket status. Please try again.");
    } finally {
      setProcessingTickets(prev => {
        const newSet = new Set(prev);
        newSet.delete(ticketId);
        return newSet;
      });
    }
  };

  const handleDeleteTicket = async (ticketId) => {
    if (!window.confirm("Are you sure you want to permanently delete this ticket? This action cannot be undone.")) {
      return;
    }
    
    setProcessingTickets(prev => new Set([...prev, ticketId]));
    try {
      await deleteTicket(ticketId);
      // Refresh the tickets list to remove the deleted ticket
      await fetchOpenTickets();
      showSuccess('Ticket deleted successfully!');
    } catch (error) {
      console.error("Error deleting ticket:", error);
      setErrorTickets("Failed to delete ticket.");
      showError("Failed to delete ticket. Please try again.");
    } finally {
      setProcessingTickets(prev => {
        const newSet = new Set(prev);
        newSet.delete(ticketId);
        return newSet;
      });
    }
  };

  useEffect(() => {
    document.title = "SuperConfig - Dashboard";
    
    const fetchAllData = async () => {
      // Fetch events and tickets first
      const [eventsResult, ticketsResult] = await Promise.allSettled([
        (async () => {
          try {
            setLoadingEvents(true);
            const data = await get("/upcoming_events");
            if (data.events) {
              setUpcomingEvents(data.events);
              return data.events;
            } else {
              setUpcomingEvents([]);
              return [];
            }
          } catch (error) {
            console.error("Error fetching upcoming events:", error);
            setUpcomingEvents([]);
            return [];
          } finally {
            setLoadingEvents(false);
          }
        })(),
        
        (async () => {
          try {
            setLoadingTickets(true);
            const data = await getAllTickets();
            setOpenTickets(data);
            return data;
          } catch (error) {
            console.error("Error fetching tickets:", error);
            setErrorTickets("Failed to load tickets.");
            return [];
          } finally {
            setLoadingTickets(false);
          }
        })()
      ]);

      // Get the results
      const events = eventsResult.status === 'fulfilled' ? eventsResult.value : [];
      const tickets = ticketsResult.status === 'fulfilled' ? ticketsResult.value : [];
      
      // Now fetch daily digest with the actual data
      await fetchDailyDigest(events, tickets);
    };

    fetchAllData();
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
              {!loadingEvents && upcomingEvents.length === 0 && (
                <p className="text-responsive-sm text-gray-600">No upcoming events.</p>
              )}
              {!loadingEvents && upcomingEvents.length > 0 && (
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
                <p className="text-responsive-sm text-gray-600">No tickets found.</p>
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
                        <th
                          scope="col"
                          className="px-2 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                          Actions
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
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              ticket.status === 'open' ? 'bg-green-100 text-green-800' :
                              ticket.status === 'closed' ? 'bg-gray-100 text-gray-800' :
                              'bg-blue-100 text-blue-800'
                            }`}>
                              {ticket.status}
                            </span>
                          </td>
                          <td className="px-2 md:px-6 py-4 text-responsive-xs text-gray-500">
                            <div className="flex space-x-2">
                              <button
                                onClick={() => handleToggleTicketStatus(ticket.id)}
                                disabled={processingTickets.has(ticket.id)}
                                className={`inline-flex items-center px-2 py-1 border border-transparent text-xs leading-4 font-medium rounded-md text-white focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed touch-target ${
                                  ticket.status === 'open' 
                                    ? 'bg-orange-600 hover:bg-orange-700 focus:ring-orange-500'
                                    : 'bg-green-600 hover:bg-green-700 focus:ring-green-500'
                                }`}
                                title={ticket.status === 'open' ? 'Close ticket' : 'Reopen ticket'}
                              >
                                {processingTickets.has(ticket.id) ? (
                                  <div className="animate-spin rounded-full h-3 w-3 border-t-2 border-b-2 border-white" />
                                ) : (
                                  <>
                                    {ticket.status === 'open' ? (
                                      <>
                                        <CheckIcon className="w-3 h-3 mr-1" />
                                        <span className="hidden sm:inline">Close</span>
                                      </>
                                    ) : (
                                      <>
                                        <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                        </svg>
                                        <span className="hidden sm:inline">Open</span>
                                      </>
                                    )}
                                  </>
                                )}
                              </button>
                              <button
                                onClick={() => handleDeleteTicket(ticket.id)}
                                disabled={processingTickets.has(ticket.id)}
                                className="inline-flex items-center px-2 py-1 border border-transparent text-xs leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed touch-target"
                                title="Delete ticket permanently"
                              >
                                {processingTickets.has(ticket.id) ? (
                                  <div className="animate-spin rounded-full h-3 w-3 border-t-2 border-b-2 border-white" />
                                ) : (
                                  <>
                                    <DeleteIcon className="w-3 h-3 mr-1" />
                                    <span className="hidden sm:inline">Delete</span>
                                  </>
                                )}
                              </button>
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
              <div className="mb-4 text-responsive-base font-semibold">Insights</div>
              {loadingDigest && <p className="text-responsive-sm">Loading insights...</p>}
              {errorDigest && <p className="text-red-500 text-responsive-sm">{errorDigest}</p>}
              {!loadingDigest && !errorDigest && !dailyDigest && (
                <p className="text-responsive-sm text-gray-600">No insights available.</p>
              )}
              {!loadingDigest && !errorDigest && dailyDigest && (
                <div 
                  className={`text-responsive-sm p-3 md:p-4 rounded-md border ${
                    dailyDigest.includes("No data is found today") 
                      ? "bg-blue-50 border-blue-200 text-blue-800" 
                      : "bg-gray-50 border-gray-200"
                  }`}
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
      {toast.show && (
        <Toast
          type={toast.type}
          title={toast.title}
          message={toast.message}
          onClose={() => setToast({ ...toast, show: false })}
        />
      )}
    </div>
  );
};

export default DashboardPage;



// @router.get("/dashboard/tickets/open", response_model=List[Dict])


// @router.get("/dashboard/customers/summaries", response_model=List[Dict])


// @router.get("/dashboard/daily_digest")


// @router.get("/upcoming_events")
