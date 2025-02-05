// "use client";
// import { Card } from "@/components/ui/card";
// import { Button } from "@/components/ui/button";
// import { Badge } from "@/components/ui/badge";
// import { ScrollArea } from "@/components/ui/scroll-area";
// import { approveAgent, rejectAgent } from "./actions";
// import { Agent } from "@/lib/marketplace-api";
// import Link from "next/link";
// import { useState } from "react";
// import { Input } from "@/components/ui/input";

// function AdminMarketplaceCard({ agent }: { agent: Agent }) {
//   const [isApproved, setIsApproved] = useState(false);
//   const [isRejected, setIsRejected] = useState(false);
//   const [comment, setComment] = useState("");

//   const approveAgentWithId = approveAgent.bind(
//     null,
//     agent.id,
//     agent.version,
//     comment,
//   );
//   const rejectAgentWithId = rejectAgent.bind(
//     null,
//     agent.id,
//     agent.version,
//     comment,
//   );

//   const handleApprove = async (e: React.FormEvent) => {
//     e.preventDefault();
//     await approveAgentWithId();
//     setIsApproved(true);
//   };

//   const handleReject = async (e: React.FormEvent) => {
//     e.preventDefault();
//     await rejectAgentWithId();
//     setIsRejected(true);
//   };

//   return (
//     <>
//       {!isApproved && !isRejected && (
//         <Card key={agent.id} className="m-3 flex h-[300px] flex-col p-4">
//           <div className="mb-2 flex items-start justify-between">
//             <Link
//               href={`/marketplace/${agent.id}`}
//               className="text-lg font-semibold hover:underline"
//             >
//               {agent.name}
//             </Link>
//             <Badge variant="outline">v{agent.version}</Badge>
//           </div>
//           <p className="mb-2 text-sm text-gray-500">by {agent.author}</p>
//           <ScrollArea className="grow">
//             <p className="mb-2 text-sm text-gray-600">{agent.description}</p>
//             <div className="mb-2 flex flex-wrap gap-1">
//               {agent.categories.map((category) => (
//                 <Badge key={category} variant="secondary">
//                   {category}
//                 </Badge>
//               ))}
//             </div>
//             <div className="flex flex-wrap gap-1">
//               {agent.keywords.map((keyword) => (
//                 <Badge key={keyword} variant="outline">
//                   {keyword}
//                 </Badge>
//               ))}
//             </div>
//           </ScrollArea>
//           <div className="mb-2 flex justify-between text-xs text-gray-500">
//             <span>
//               Created: {new Date(agent.createdAt).toLocaleDateString()}
//             </span>
//             <span>
//               Updated: {new Date(agent.updatedAt).toLocaleDateString()}
//             </span>
//           </div>
//           <div className="mb-4 flex justify-between text-sm">
//             <span>👁 {agent.views}</span>
//             <span>⬇️ {agent.downloads}</span>
//           </div>
//           <div className="mt-auto space-y-2">
//             <div className="flex justify-end space-x-2">
//               <Input
//                 type="text"
//                 placeholder="Add a comment (optional)"
//                 value={comment}
//                 onChange={(e) => setComment(e.target.value)}
//               />
//               {!isRejected && (
//                 <form onSubmit={handleReject}>
//                   <Button variant="outline" type="submit">
//                     Reject
//                   </Button>
//                 </form>
//               )}
//               {!isApproved && (
//                 <form onSubmit={handleApprove}>
//                   <Button type="submit">Approve</Button>
//                 </form>
//               )}
//             </div>
//           </div>
//         </Card>
//       )}
//     </>
//   );
// }

// export default AdminMarketplaceCard;
