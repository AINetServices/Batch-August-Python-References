-- Allow authenticated users to upload files
CREATE POLICY "Allow authenticated upload to resumes"
ON storage.objects
FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'resumes');

-- Allow authenticated users to read files  
CREATE POLICY "Allow authenticated read from resumes"
ON storage.objects
FOR SELECT
TO authenticated
USING (bucket_id = 'resumes');

-- Allow authenticated users to update files
CREATE POLICY "Allow authenticated update to resumes"
ON storage.objects
FOR UPDATE
TO authenticated
USING (bucket_id = 'resumes');

-- Allow authenticated users to delete files
CREATE POLICY "Allow authenticated delete from resumes"
ON storage.objects
FOR DELETE
TO authenticated
USING (bucket_id = 'resumes');