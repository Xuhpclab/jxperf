package org.apache.lucene.search;

/**
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import org.apache.lucene.util.LuceneTestCase;
import org.apache.lucene.analysis.SimpleAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.index.*;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.MockRAMDirectory;
import org.apache.lucene.util.English;

import java.io.IOException;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.SortedSet;

public class TestTermVectors extends LuceneTestCase {
  private IndexSearcher searcher;
  private Directory directory = new MockRAMDirectory();
  public TestTermVectors(String s) {
    super(s);
  }

  public void setUp() throws Exception {                  
    super.setUp();
    IndexWriter writer = new IndexWriter(directory, new SimpleAnalyzer(), true,
                                         IndexWriter.MaxFieldLength.LIMITED);
    //writer.setUseCompoundFile(true);
    //writer.infoStream = System.out;
    for (int i = 0; i < 1000; i++) {
      Document doc = new Document();
      Field.TermVector termVector;
      int mod3 = i % 3;
      int mod2 = i % 2;
      if (mod2 == 0 && mod3 == 0){
        termVector = Field.TermVector.WITH_POSITIONS_OFFSETS;
      }
      else if (mod2 == 0){
        termVector = Field.TermVector.WITH_POSITIONS;
      }
      else if (mod3 == 0){
        termVector = Field.TermVector.WITH_OFFSETS;
      }
      else {
        termVector = Field.TermVector.YES;
      }
      doc.add(new Field("field", English.intToEnglish(i),
          Field.Store.YES, Field.Index.ANALYZED, termVector));
      writer.addDocument(doc);
    }
    writer.close();
    searcher = new IndexSearcher(directory);
  }

  public void test() {
    assertTrue(searcher != null);
  }

  public void testTermVectors() {
    Query query = new TermQuery(new Term("field", "seventy"));
    try {
      ScoreDoc[] hits = searcher.search(query, null, 1000).scoreDocs;
      assertEquals(100, hits.length);
      
      for (int i = 0; i < hits.length; i++)
      {
        TermFreqVector [] vector = searcher.reader.getTermFreqVectors(hits[i].doc);
        assertTrue(vector != null);
        assertTrue(vector.length == 1);
      }
    } catch (IOException e) {
      assertTrue(false);
    }
  }
  
  public void testTermVectorsFieldOrder() throws IOException {
    Directory dir = new MockRAMDirectory();
    IndexWriter writer = new IndexWriter(dir, new SimpleAnalyzer(), true, IndexWriter.MaxFieldLength.LIMITED);
    Document doc = new Document();
    doc.add(new Field("c", "some content here", Field.Store.YES, Field.Index.ANALYZED, Field.TermVector.WITH_POSITIONS_OFFSETS));
    doc.add(new Field("a", "some content here", Field.Store.YES, Field.Index.ANALYZED, Field.TermVector.WITH_POSITIONS_OFFSETS));
    doc.add(new Field("b", "some content here", Field.Store.YES, Field.Index.ANALYZED, Field.TermVector.WITH_POSITIONS_OFFSETS));
    doc.add(new Field("x", "some content here", Field.Store.YES, Field.Index.ANALYZED, Field.TermVector.WITH_POSITIONS_OFFSETS));
    writer.addDocument(doc);
    writer.close();
    IndexReader reader = IndexReader.open(dir);
    TermFreqVector[] v = reader.getTermFreqVectors(0);
    assertEquals(4, v.length);
    String[] expectedFields = new String[]{"a", "b", "c", "x"};
    int[] expectedPositions = new int[]{1, 2, 0};
    for(int i=0;i<v.length;i++) {
      TermPositionVector posVec = (TermPositionVector) v[i];
      assertEquals(expectedFields[i], posVec.getField());
      String[] terms = posVec.getTerms();
      assertEquals(3, terms.length);
      assertEquals("content", terms[0]);
      assertEquals("here", terms[1]);
      assertEquals("some", terms[2]);
      for(int j=0;j<3;j++) {
        int[] positions = posVec.getTermPositions(j);
        assertEquals(1, positions.length);
        assertEquals(expectedPositions[j], positions[0]);
      }
    }
  }

  public void testTermPositionVectors() {
    Query query = new TermQuery(new Term("field", "zero"));
    try {
      ScoreDoc[] hits = searcher.search(query, null, 1000).scoreDocs;
      assertEquals(1, hits.length);
      
      for (int i = 0; i < hits.length; i++)
      {
        TermFreqVector [] vector = searcher.reader.getTermFreqVectors(hits[i].doc);
        assertTrue(vector != null);
        assertTrue(vector.length == 1);
        
        boolean shouldBePosVector = (hits[i].doc % 2 == 0) ? true : false;
        assertTrue((shouldBePosVector == false) || (shouldBePosVector == true && (vector[0] instanceof TermPositionVector == true)));
       
        boolean shouldBeOffVector = (hits[i].doc % 3 == 0) ? true : false;
        assertTrue((shouldBeOffVector == false) || (shouldBeOffVector == true && (vector[0] instanceof TermPositionVector == true)));
        
        if(shouldBePosVector || shouldBeOffVector){
          TermPositionVector posVec = (TermPositionVector)vector[0];
          String [] terms = posVec.getTerms();
          assertTrue(terms != null && terms.length > 0);
          
          for (int j = 0; j < terms.length; j++) {
            int [] positions = posVec.getTermPositions(j);
            TermVectorOffsetInfo [] offsets = posVec.getOffsets(j);
            
            if(shouldBePosVector){
              assertTrue(positions != null);
              assertTrue(positions.length > 0);
            }
            else
              assertTrue(positions == null);
            
            if(shouldBeOffVector){
              assertTrue(offsets != null);
              assertTrue(offsets.length > 0);
            }
            else
              assertTrue(offsets == null);
          }
        }
        else{
          try{
            TermPositionVector posVec = (TermPositionVector)vector[0];
            assertTrue(false);
          }
          catch(ClassCastException ignore){
            TermFreqVector freqVec = vector[0];
            String [] terms = freqVec.getTerms();
            assertTrue(terms != null && terms.length > 0);
          }
          
        }
       
      }
    } catch (IOException e) {
      assertTrue(false);
    }
  }
  
  public void testTermOffsetVectors() {
    Query query = new TermQuery(new Term("field", "fifty"));
    try {
      ScoreDoc[] hits = searcher.search(query, null, 1000).scoreDocs;
      assertEquals(100, hits.length);
      
      for (int i = 0; i < hits.length; i++)
      {
        TermFreqVector [] vector = searcher.reader.getTermFreqVectors(hits[i].doc);
        assertTrue(vector != null);
        assertTrue(vector.length == 1);
        
        //assertTrue();
      }
    } catch (IOException e) {
      assertTrue(false);
    }
  }

  public void testKnownSetOfDocuments() {
    String test1 = "eating chocolate in a computer lab"; //6 terms
    String test2 = "computer in a computer lab"; //5 terms
    String test3 = "a chocolate lab grows old"; //5 terms
    String test4 = "eating chocolate with a chocolate lab in an old chocolate colored computer lab"; //13 terms
    Map test4Map = new HashMap();
    test4Map.put("chocolate", new Integer(3));
    test4Map.put("lab", new Integer(2));
    test4Map.put("eating", new Integer(1));
    test4Map.put("computer", new Integer(1));
    test4Map.put("with", new Integer(1));
    test4Map.put("a", new Integer(1));
    test4Map.put("colored", new Integer(1));
    test4Map.put("in", new Integer(1));
    test4Map.put("an", new Integer(1));
    test4Map.put("computer", new Integer(1));
    test4Map.put("old", new Integer(1));
    
    Document testDoc1 = new Document();
    setupDoc(testDoc1, test1);
    Document testDoc2 = new Document();
    setupDoc(testDoc2, test2);
    Document testDoc3 = new Document();
    setupDoc(testDoc3, test3);
    Document testDoc4 = new Document();
    setupDoc(testDoc4, test4);
        
    Directory dir = new MockRAMDirectory();
    
    try {
      IndexWriter writer = new IndexWriter(dir, new SimpleAnalyzer(), true, 
                                           IndexWriter.MaxFieldLength.LIMITED);
      assertTrue(writer != null);
      writer.addDocument(testDoc1);
      writer.addDocument(testDoc2);
      writer.addDocument(testDoc3);
      writer.addDocument(testDoc4);
      writer.close();
      IndexSearcher knownSearcher = new IndexSearcher(dir);
      TermEnum termEnum = knownSearcher.reader.terms();
      TermDocs termDocs = knownSearcher.reader.termDocs();
      //System.out.println("Terms: " + termEnum.size() + " Orig Len: " + termArray.length);
      
      Similarity sim = knownSearcher.getSimilarity();
      while (termEnum.next() == true)
      {
        Term term = termEnum.term();
        //System.out.println("Term: " + term);
        termDocs.seek(term);
        while (termDocs.next())
        {
          int docId = termDocs.doc();
          int freq = termDocs.freq();
          //System.out.println("Doc Id: " + docId + " freq " + freq);
          TermFreqVector vector = knownSearcher.reader.getTermFreqVector(docId, "field");
          float tf = sim.tf(freq);
          float idf = sim.idf(term, knownSearcher);
          //float qNorm = sim.queryNorm()
          //This is fine since we don't have stop words
          float lNorm = sim.lengthNorm("field", vector.getTerms().length);
          //float coord = sim.coord()
          //System.out.println("TF: " + tf + " IDF: " + idf + " LenNorm: " + lNorm);
          assertTrue(vector != null);
          String[] vTerms = vector.getTerms();
          int [] freqs = vector.getTermFrequencies();
          for (int i = 0; i < vTerms.length; i++)
          {
            if (term.text().equals(vTerms[i]))
            {
              assertTrue(freqs[i] == freq);
            }
          }
          
        }
        //System.out.println("--------");
      }
      Query query = new TermQuery(new Term("field", "chocolate"));
      ScoreDoc[] hits = knownSearcher.search(query, null, 1000).scoreDocs;
      //doc 3 should be the first hit b/c it is the shortest match
      assertTrue(hits.length == 3);
      float score = hits[0].score;
      /*System.out.println("Hit 0: " + hits.id(0) + " Score: " + hits.score(0) + " String: " + hits.doc(0).toString());
      System.out.println("Explain: " + knownSearcher.explain(query, hits.id(0)));
      System.out.println("Hit 1: " + hits.id(1) + " Score: " + hits.score(1) + " String: " + hits.doc(1).toString());
      System.out.println("Explain: " + knownSearcher.explain(query, hits.id(1)));
      System.out.println("Hit 2: " + hits.id(2) + " Score: " + hits.score(2) + " String: " +  hits.doc(2).toString());
      System.out.println("Explain: " + knownSearcher.explain(query, hits.id(2)));*/
      assertTrue(hits[0].doc == 2);
      assertTrue(hits[1].doc == 3);
      assertTrue(hits[2].doc == 0);
      TermFreqVector vector = knownSearcher.reader.getTermFreqVector(hits[1].doc, "field");
      assertTrue(vector != null);
      //System.out.println("Vector: " + vector);
      String[] terms = vector.getTerms();
      int [] freqs = vector.getTermFrequencies();
      assertTrue(terms != null && terms.length == 10);
      for (int i = 0; i < terms.length; i++) {
        String term = terms[i];
        //System.out.println("Term: " + term);
        int freq = freqs[i];
        assertTrue(test4.indexOf(term) != -1);
        Integer freqInt = (Integer)test4Map.get(term);
        assertTrue(freqInt != null);
        assertTrue(freqInt.intValue() == freq);        
      }
      SortedTermVectorMapper mapper = new SortedTermVectorMapper(new TermVectorEntryFreqSortedComparator());
      knownSearcher.reader.getTermFreqVector(hits[1].doc, mapper);
      SortedSet vectorEntrySet = mapper.getTermVectorEntrySet();
      assertTrue("mapper.getTermVectorEntrySet() Size: " + vectorEntrySet.size() + " is not: " + 10, vectorEntrySet.size() == 10);
      TermVectorEntry last = null;
      for (Iterator iterator = vectorEntrySet.iterator(); iterator.hasNext();) {
         TermVectorEntry tve = (TermVectorEntry) iterator.next();
        if (tve != null && last != null)
        {
          assertTrue("terms are not properly sorted", last.getFrequency() >= tve.getFrequency());
          Integer expectedFreq = (Integer) test4Map.get(tve.getTerm());
          //we expect double the expectedFreq, since there are two fields with the exact same text and we are collapsing all fields
          assertTrue("Frequency is not correct:", tve.getFrequency() == 2*expectedFreq.intValue());
        }
        last = tve;

      }

      FieldSortedTermVectorMapper fieldMapper = new FieldSortedTermVectorMapper(new TermVectorEntryFreqSortedComparator());
      knownSearcher.reader.getTermFreqVector(hits[1].doc, fieldMapper);
      Map map = fieldMapper.getFieldToTerms();
      assertTrue("map Size: " + map.size() + " is not: " + 2, map.size() == 2);
      vectorEntrySet = (SortedSet) map.get("field");
      assertTrue("vectorEntrySet is null and it shouldn't be", vectorEntrySet != null);
      assertTrue("vectorEntrySet Size: " + vectorEntrySet.size() + " is not: " + 10, vectorEntrySet.size() == 10);
      knownSearcher.close();
    } catch (IOException e) {
      e.printStackTrace();
      assertTrue(false);
    }
  } 
  
  private void setupDoc(Document doc, String text)
  {
    doc.add(new Field("field2", text, Field.Store.YES,
        Field.Index.ANALYZED, Field.TermVector.WITH_POSITIONS_OFFSETS));
    doc.add(new Field("field", text, Field.Store.YES,
        Field.Index.ANALYZED, Field.TermVector.YES));
    //System.out.println("Document: " + doc);
  }

  // Test only a few docs having vectors
  public void testRareVectors() throws IOException {
    IndexWriter writer = new IndexWriter(directory, new SimpleAnalyzer(), true, 
                                         IndexWriter.MaxFieldLength.LIMITED);
    for(int i=0;i<100;i++) {
      Document doc = new Document();
      doc.add(new Field("field", English.intToEnglish(i),
                        Field.Store.YES, Field.Index.ANALYZED, Field.TermVector.NO));
      writer.addDocument(doc);
    }
    for(int i=0;i<10;i++) {
      Document doc = new Document();
      doc.add(new Field("field", English.intToEnglish(100+i),
                        Field.Store.YES, Field.Index.ANALYZED, Field.TermVector.WITH_POSITIONS_OFFSETS));
      writer.addDocument(doc);
    }

    writer.close();
    searcher = new IndexSearcher(directory);

    Query query = new TermQuery(new Term("field", "hundred"));
    ScoreDoc[] hits = searcher.search(query, null, 1000).scoreDocs;
    assertEquals(10, hits.length);
    for (int i = 0; i < hits.length; i++) {
      TermFreqVector [] vector = searcher.reader.getTermFreqVectors(hits[i].doc);
      assertTrue(vector != null);
      assertTrue(vector.length == 1);
    }
  }


  // In a single doc, for the same field, mix the term
  // vectors up
  public void testMixedVectrosVectors() throws IOException {
    IndexWriter writer = new IndexWriter(directory, new SimpleAnalyzer(), true, 
                                         IndexWriter.MaxFieldLength.LIMITED);
    Document doc = new Document();
    doc.add(new Field("field", "one",
                      Field.Store.YES, Field.Index.ANALYZED, Field.TermVector.NO));
    doc.add(new Field("field", "one",
                      Field.Store.YES, Field.Index.ANALYZED, Field.TermVector.YES));
    doc.add(new Field("field", "one",
                      Field.Store.YES, Field.Index.ANALYZED, Field.TermVector.WITH_POSITIONS));
    doc.add(new Field("field", "one",
                      Field.Store.YES, Field.Index.ANALYZED, Field.TermVector.WITH_OFFSETS));
    doc.add(new Field("field", "one",
                      Field.Store.YES, Field.Index.ANALYZED, Field.TermVector.WITH_POSITIONS_OFFSETS));
    writer.addDocument(doc);
    writer.close();

    searcher = new IndexSearcher(directory);

    Query query = new TermQuery(new Term("field", "one"));
    ScoreDoc[] hits = searcher.search(query, null, 1000).scoreDocs;
    assertEquals(1, hits.length);

    TermFreqVector [] vector = searcher.reader.getTermFreqVectors(hits[0].doc);
    assertTrue(vector != null);
    assertTrue(vector.length == 1);
    TermPositionVector tfv = (TermPositionVector) vector[0];
    assertTrue(tfv.getField().equals("field"));
    String[] terms = tfv.getTerms();
    assertEquals(1, terms.length);
    assertEquals(terms[0], "one");
    assertEquals(5, tfv.getTermFrequencies()[0]);

    int[] positions = tfv.getTermPositions(0);
    assertEquals(5, positions.length);
    for(int i=0;i<5;i++)
      assertEquals(i, positions[i]);
    TermVectorOffsetInfo[] offsets = tfv.getOffsets(0);
    assertEquals(5, offsets.length);
    for(int i=0;i<5;i++) {
      assertEquals(4*i, offsets[i].getStartOffset());
      assertEquals(4*i+3, offsets[i].getEndOffset());
    }
  }
}
