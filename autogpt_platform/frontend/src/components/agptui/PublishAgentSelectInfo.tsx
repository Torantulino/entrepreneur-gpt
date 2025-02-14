"use client";

import * as React from "react";
import Image from "next/image";
import { Button } from "../agptui/Button";
import { IconClose, IconPlus } from "../ui/icons";
import BackendAPI from "@/lib/autogpt-server-api";

export interface PublishAgentInfoInitialData {
  agent_id: string;
  title: string;
  subheader: string;
  slug: string;
  thumbnailSrc: string;
  youtubeLink: string;
  category: string;
  description: string;
  additionalImages?: string[];
}

interface PublishAgentInfoProps {
  onBack: () => void;
  onSubmit: (
    name: string,
    subHeading: string,
    slug: string,
    description: string,
    imageUrls: string[],
    videoUrl: string,
    categories: string[],
  ) => void;
  onClose: () => void;
  initialData?: PublishAgentInfoInitialData;
}

export const PublishAgentInfo: React.FC<PublishAgentInfoProps> = ({
  onBack,
  onSubmit,
  onClose,
  initialData,
}) => {
  const [agentId, setAgentId] = React.useState<string | null>(null);
  const [images, setImages] = React.useState<string[]>(
    initialData?.additionalImages
      ? [initialData.thumbnailSrc, ...initialData.additionalImages]
      : initialData?.thumbnailSrc
        ? [initialData.thumbnailSrc]
        : [],
  );
  const [selectedImage, setSelectedImage] = React.useState<string | null>(
    initialData?.thumbnailSrc || null,
  );
  const [title, setTitle] = React.useState(initialData?.title || "");
  const [subheader, setSubheader] = React.useState(
    initialData?.subheader || "",
  );
  const [youtubeLink, setYoutubeLink] = React.useState(
    initialData?.youtubeLink || "",
  );
  const [category, setCategory] = React.useState(initialData?.category || "");
  const [description, setDescription] = React.useState(
    initialData?.description || "",
  );
  const [slug, setSlug] = React.useState(initialData?.slug || "");
  const thumbnailsContainerRef = React.useRef<HTMLDivElement | null>(null);
  React.useEffect(() => {
    if (initialData) {
      setAgentId(initialData.agent_id);
      setImagesWithValidation(initialData.additionalImages || []);
      setSelectedImage(initialData.thumbnailSrc || null);
      setTitle(initialData.title);
      setSubheader(initialData.subheader);
      setYoutubeLink(initialData.youtubeLink);
      setCategory(initialData.category);
      setDescription(initialData.description);
      setSlug(initialData.slug);
    }
  }, [initialData]);

  const setImagesWithValidation = (newImages: string[]) => {
    // Remove duplicates
    const uniqueImages = Array.from(new Set(newImages));
    // Keep only first 5 images
    const limitedImages = uniqueImages.slice(0, 5);
    setImages(limitedImages);
  };

  const handleRemoveImage = (indexToRemove: number) => {
    const newImages = [...images];
    newImages.splice(indexToRemove, 1);
    setImagesWithValidation(newImages);
    if (newImages[indexToRemove] === selectedImage) {
      setSelectedImage(newImages[0] || null);
    }
    if (newImages.length === 0) {
      setSelectedImage(null);
    } else {
      console.log("images", newImages);
    }
  };

  const handleAddImage = async () => {
    if (images.length >= 5) return;

    const input = document.createElement("input");
    input.type = "file";
    input.accept = "image/*";

    // Create a promise that resolves when file is selected
    const fileSelected = new Promise<File | null>((resolve) => {
      input.onchange = (e) => {
        const file = (e.target as HTMLInputElement).files?.[0];
        resolve(file || null);
      };
    });

    // Trigger file selection
    input.click();

    // Wait for file selection
    const file = await fileSelected;
    if (!file) return;

    try {
      const api = new BackendAPI();

      const imageUrl = (await api.uploadStoreSubmissionMedia(file)).replace(
        /^"(.*)"$/,
        "$1",
      );

      setImagesWithValidation([...images, imageUrl]);
      if (!selectedImage) {
        setSelectedImage(imageUrl);
      }
    } catch (error) {
      console.error("Error uploading image:", error);
    }
  };

  const [isGenerating, setIsGenerating] = React.useState(false);

  const handleGenerateImage = async () => {
    if (isGenerating || images.length >= 5) return;

    setIsGenerating(true);
    try {
      const api = new BackendAPI();
      if (!agentId) {
        throw new Error("Agent ID is required");
      }
      const { image_url } = await api.generateStoreSubmissionImage(agentId);
      console.log("image_url", image_url);
      setImagesWithValidation([...images, image_url]);
    } catch (error) {
      console.error("Failed to generate image:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSubmit = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    onSubmit(title, subheader, slug, description, images, youtubeLink, [
      category,
    ]);
  };

  return (
    <div className="mx-auto flex w-full flex-col rounded-3xl bg-white dark:bg-gray-800">
      <div className="relative p-6">
        <div className="absolute right-4 top-2">
          <button
            onClick={onClose}
            className="flex h-[38px] w-[38px] items-center justify-center rounded-full bg-gray-100 transition-colors hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600"
            aria-label="Close"
          >
            <IconClose
              size="default"
              className="text-neutral-600 dark:text-neutral-300"
            />
          </button>
        </div>
        <h3 className="h3-poppins text-center text-2xl font-semibold leading-loose text-neutral-900 dark:text-neutral-100">
          Publish Agent
        </h3>
        <p className="p text-center text-base font-normal leading-7 text-neutral-600 dark:text-neutral-400">
          Write a bit of details about your agent
        </p>
      </div>

      <div className="flex-grow space-y-5 overflow-y-auto p-6">
        <div className="space-y-1.5">
          <label
            htmlFor="title"
            className="text-sm font-medium leading-tight text-slate-950 dark:text-slate-300"
          >
            Title
          </label>
          <input
            id="title"
            type="text"
            placeholder="Agent name"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="p-ui-medium w-full rounded-[55px] border border-slate-200 py-2.5 pl-4 pr-14 text-base font-normal leading-normal text-slate-500 dark:border-slate-700 dark:bg-gray-700 dark:text-slate-300"
          />
        </div>

        <div className="space-y-1.5">
          <label
            htmlFor="subheader"
            className="text-sm font-medium leading-tight text-slate-950 dark:text-slate-300"
          >
            Subheader
          </label>
          <input
            id="subheader"
            type="text"
            placeholder="A tagline for your agent"
            value={subheader}
            onChange={(e) => setSubheader(e.target.value)}
            className="w-full rounded-[55px] border border-slate-200 py-2.5 pl-4 pr-14 font-['Geist'] text-base font-normal leading-normal text-slate-500 dark:border-slate-700 dark:bg-gray-700 dark:text-slate-300"
          />
        </div>

        <div className="space-y-1.5">
          <label
            htmlFor="slug"
            className="text-sm font-medium leading-tight text-slate-950 dark:text-slate-300"
          >
            Slug
          </label>
          <input
            id="slug"
            type="text"
            placeholder="URL-friendly name for your agent"
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
            className="w-full rounded-[55px] border border-slate-200 py-2.5 pl-4 pr-14 font-['Geist'] text-base font-normal leading-normal text-slate-500 dark:border-slate-700 dark:bg-gray-700 dark:text-slate-300"
          />
        </div>

        <div className="space-y-2.5">
          <label className="text-sm font-medium leading-tight text-slate-950 dark:text-slate-300">
            Thumbnail images
          </label>
          <div className="flex h-[350px] items-center justify-center overflow-hidden rounded-[20px] border border-neutral-300 p-2.5 dark:border-neutral-600">
            {selectedImage !== null && selectedImage !== undefined ? (
              <Image
                src={selectedImage}
                alt="Selected Thumbnail"
                width={500}
                height={350}
                style={{ objectFit: "cover" }}
                className="rounded-md"
              />
            ) : (
              <p className="font-['Geist'] text-sm font-normal text-neutral-600 dark:text-neutral-400">
                No images yet
              </p>
            )}
          </div>
          <div
            ref={thumbnailsContainerRef}
            className="flex items-center space-x-2 overflow-x-auto"
          >
            {images.length === 0 ? (
              <div className="flex w-full justify-center">
                <Button
                  onClick={handleAddImage}
                  variant="ghost"
                  className="flex h-[70px] w-[100px] flex-col items-center justify-center rounded-md bg-neutral-200 hover:bg-neutral-300 dark:bg-neutral-700 dark:hover:bg-neutral-600"
                >
                  <label htmlFor="image-upload" className="cursor-pointer">
                    <input
                      id="image-upload"
                      type="file"
                      accept="image/*"
                      onChange={handleAddImage}
                      className="hidden"
                    />
                    <IconPlus
                      size="lg"
                      className="text-neutral-600 dark:text-neutral-300"
                    />
                    <span className="mt-1 font-['Geist'] text-xs font-normal text-neutral-600 dark:text-neutral-300">
                      Add image
                    </span>
                  </label>
                </Button>
              </div>
            ) : (
              <>
                {images.map((src, index) => (
                  <div key={index} className="relative flex-shrink-0">
                    <Image
                      src={src}
                      alt={`Thumbnail ${index + 1}`}
                      width={100}
                      height={70}
                      style={{ objectFit: "cover" }}
                      className="cursor-pointer rounded-md"
                      onClick={() => setSelectedImage(src)}
                    />
                    <button
                      onClick={() => handleRemoveImage(index)}
                      className="absolute right-1 top-1 flex h-5 w-5 items-center justify-center rounded-full bg-white bg-opacity-70 transition-opacity hover:bg-opacity-100 dark:bg-gray-800 dark:bg-opacity-70 dark:hover:bg-opacity-100"
                      aria-label="Remove image"
                    >
                      <IconClose
                        size="sm"
                        className="text-neutral-600 dark:text-neutral-300"
                      />
                    </button>
                  </div>
                ))}
                {images.length < 5 && (
                  <Button
                    onClick={handleAddImage}
                    variant="ghost"
                    className="flex h-[70px] w-[100px] flex-col items-center justify-center rounded-md bg-neutral-200 hover:bg-neutral-300 dark:bg-neutral-700 dark:hover:bg-neutral-600"
                  >
                    <IconPlus
                      size="lg"
                      className="text-neutral-600 dark:text-neutral-300"
                    />
                    <span className="mt-1 font-['Geist'] text-xs font-normal text-neutral-600 dark:text-neutral-300">
                      Add image
                    </span>
                  </Button>
                )}
              </>
            )}
          </div>
        </div>

        <div className="space-y-1.5">
          <label className="text-sm font-medium leading-tight text-slate-950 dark:text-slate-300">
            AI image generator
          </label>
          <div className="flex items-center justify-between">
            <p className="text-base font-normal leading-normal text-slate-700 dark:text-slate-400">
              You can use AI to generate a cover image for you
            </p>
            <Button
              size="sm"
              className={`bg-neutral-800 text-white hover:bg-neutral-900 dark:bg-neutral-600 dark:hover:bg-neutral-500 ${
                images.length >= 5 ? "cursor-not-allowed opacity-50" : ""
              }`}
              onClick={handleGenerateImage}
              disabled={isGenerating || images.length >= 5}
            >
              {isGenerating
                ? "Generating..."
                : images.length >= 5
                  ? "Max images reached"
                  : "Generate"}
            </Button>
          </div>
        </div>

        <div className="space-y-1.5">
          <label
            htmlFor="youtube"
            className="text-sm font-medium leading-tight text-slate-950 dark:text-slate-300"
          >
            YouTube video link
          </label>
          <input
            id="youtube"
            type="text"
            placeholder="Paste a video link here"
            value={youtubeLink}
            onChange={(e) => setYoutubeLink(e.target.value)}
            className="w-full rounded-[55px] border border-slate-200 py-2.5 pl-4 pr-14 font-['Geist'] text-base font-normal leading-normal text-slate-500 dark:border-slate-700 dark:bg-gray-700 dark:text-slate-300"
          />
        </div>

        <div className="space-y-1.5">
          <label
            htmlFor="category"
            className="text-sm font-medium leading-tight text-slate-950 dark:text-slate-300"
          >
            Category
          </label>
          <select
            id="category"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-full appearance-none rounded-[55px] border border-slate-200 py-2.5 pl-4 pr-5 font-['Geist'] text-base font-normal leading-normal text-slate-500 dark:border-slate-700 dark:bg-gray-700 dark:text-slate-300"
          >
            <option value="">Select a category for your agent</option>
            <option value="productivity">Productivity</option>
            <option value="writing">Writing & Content</option>
            <option value="development">Development</option>
            <option value="data">Data & Analytics</option>
            <option value="marketing">Marketing & SEO</option>
            <option value="research">Research & Learning</option>
            <option value="creative">Creative & Design</option>
            <option value="business">Business & Finance</option>
            <option value="personal">Personal Assistant</option>
            <option value="other">Other</option>
            {/* Add more options here */}
          </select>
        </div>

        <div className="space-y-1.5">
          <label
            htmlFor="description"
            className="text-sm font-medium leading-tight text-slate-950 dark:text-slate-300"
          >
            Description
          </label>
          <textarea
            id="description"
            placeholder="Describe your agent and what it does"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="h-[100px] w-full resize-none rounded-2xl border border-slate-200 bg-white py-2.5 pl-4 pr-14 font-['Geist'] text-base font-normal leading-normal text-slate-900 dark:border-slate-700 dark:bg-gray-700 dark:text-slate-300"
          ></textarea>
        </div>
      </div>

      <div className="flex justify-between gap-4 border-t border-slate-200 p-6 dark:border-slate-700">
        <Button
          onClick={onBack}
          size="default"
          className="w-full dark:border-slate-700 dark:text-slate-300 sm:flex-1"
        >
          Back
        </Button>
        <Button
          onClick={handleSubmit}
          size="default"
          className="w-full bg-neutral-800 text-white hover:bg-neutral-900 dark:bg-neutral-600 dark:hover:bg-neutral-500 sm:flex-1"
        >
          Submit for review
        </Button>
      </div>
    </div>
  );
};
