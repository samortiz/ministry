package ministryquoter;

import java.io.BufferedWriter;
import java.io.Closeable;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Scanner;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

public class QuoteFinder {

  public static final String BOOK_PATH = "docs/books";
  public static final String OUTPUT_PATH = "docs/ministryquoter/quotes";   
  
  private BufferedWriter out = null;
  
  /** 
   * @param s  String to shorten
   * @param numChars number of characters to return
   * @return the last numChars chars from the String 
   */
  public String lastChars(String str, int numChars) {
    if ((str == null) || (str.length() <= numChars)) return str;
    return str.substring((str.length() - numChars), str.length());
  }
  
  /**
   * General, initial cleaning up 
   * Remove 
   *  - HTML tags
   *  - References
   *  - End of sentence mess
   * @param str to clean
   */
  public String clean(String str) {
    String s = str;
    s = s.replaceAll("\\(.*?\\)", ""); // things in ()  (John 12:24)
    s = s.replaceAll("\\[.*?\\]", ""); // things in []  [see also...]

    // Quotes
    s = s.replaceAll("[\\u2018\\u2019\\u201C\\u201D\\u0090\\u0091\\u0092\\u0093\\u0094\\u0095\"\\u00bc\\u005e]", "'");
    
    // Foreign accents
    s = s.replaceAll("[\\u00e0\\u00e1\\u00e2\\u00e3\\u00e4\\u00e5\\u00e6]", "a"); 
    s = s.replaceAll("[\\u00c0\\u00c1\\u00c2\\u00c3\\u00c4\\u00c5\\u00c6]", "A");
    s = s.replaceAll("[\\u00c8\\u00c9\\u00ca\\u00cb]", "E");
    s = s.replaceAll("[\\u00e8\\u00e9\\u00ea\\u00eb]", "e");
    s = s.replaceAll("[\\u00d9\\u00da\\u00db\\u00dc]", "U");
    s = s.replaceAll("[\\u00f9\\u00fa\\u00fb\\u00fc]", "u");
    s = s.replaceAll("[\\u00d2\\u00d3\\u00d4\\u00d5\\u00d6]", "O");
    s = s.replaceAll("[\\u00f2\\u00f3\\u00f4\\u00f5\\u00f6]", "o");
    s = s.replaceAll("[\\u00cc\\u00cd\\u00ce\\u00cf]", "I");
    s = s.replaceAll("[\\u00ec\\u00ed\\u00ee\\u00ef]", "i");
    s = s.replaceAll("[\\u00c7]", "C");
    s = s.replaceAll("[\\u00e7]", "c");
    s = s.replaceAll("[\\u00d1]", "N");
    s = s.replaceAll("[\\u00f1]", "n");
    s = s.replaceAll("[\\u00dd]", "Y");
    s = s.replaceAll("[\\u00ff\\u00fd]", "y");
    
    s = s.replaceAll("[\\u2022]", "."); // funny dot
    s = s.replaceAll("[\\u0096\\u2014\\u00ad]", "-"); // hyphens
    s = s.replaceAll("[\\u00d7]", "x"); 
    s = s.replaceAll("[\\u00bd]", "1/2");
    s = s.replaceAll("[\\u00be]", "3/4");
    
    s = s.replaceAll("[\\*#\\u005f\\u0060\\>\\u0087\\u005b=\\u005d\\u003c]", ""); // chars to remove
    s = s.replaceAll("[\\u0097\\u2026]", " "); // chars to replace with spaces
    
    // Greek (not even trying)
    s = s.replaceAll("[\\u0370\\u0371\\u0372\\u0373\\u0374\\u0375\\u0376\\u0377\\u0378\\u0379\\u037a\\u037b\\u037c\\u037d\\u037e\\u037f]", ""); 
    s = s.replaceAll("[\\u0380\\u0381\\u0382\\u0383\\u0384\\u0385\\u0386\\u0387\\u0388\\u0389\\u038a\\u038b\\u038c\\u038d\\u038e\\u038f]", "");
    s = s.replaceAll("[\\u0390\\u0391\\u0392\\u0393\\u0394\\u0395\\u0396\\u0397\\u0398\\u0399\\u039a\\u039b\\u039c\\u039d\\u039e\\u039f]", "");
    s = s.replaceAll("[\\u03a0\\u03a1\\u03a2\\u03a3\\u03a4\\u03a5\\u03a6\\u03a7\\u03a8\\u03a9\\u03aa\\u03ab\\u03ac\\u03ad\\u03ae\\u03af]", "");
    s = s.replaceAll("[\\u03b0\\u03b1\\u03b2\\u03b3\\u03b4\\u03b5\\u03b6\\u03b7\\u03b8\\u03b9\\u03ba\\u03bb\\u03bc\\u03bd\\u03be\\u03bf]", "");
    s = s.replaceAll("[\\u03c0\\u03c1\\u03c2\\u03c3\\u03c4\\u03c5\\u03c6\\u03c7\\u03c8\\u03c9\\u03ca\\u03cb\\u03cc\\u03cd\\u03ce\\u03cf]", "");
    s = s.replaceAll("[\\u03d0\\u03d1\\u03d2\\u03d3\\u03d4\\u03d5\\u03d6\\u03d7\\u03d8\\u03d9\\u03da\\u03db\\u03dc\\u03dd\\u03de\\u03df]", "");
    s = s.replaceAll("[\\u03e0\\u03e1\\u03e2\\u03e3\\u03e4\\u03e5\\u03e6\\u03e7\\u03e8\\u03e9\\u03ea\\u03eb\\u03ec\\u03ed\\u03ee\\u03ef]", "");
    s = s.replaceAll("[\\u03f0\\u03f1\\u03f2\\u03f3\\u03f4\\u03f5\\u03f6\\u03f7\\u03f8\\u03f9\\u03fa\\u03fb\\u03fc\\u03fd\\u03fe\\u03ff]", "");
    
    // Quotes ending a sentence
    s = s.replaceAll("\\.'", "'\\."); 
    s = s.replaceAll("!'", "'!");
    s = s.replaceAll("\\?'", "'\\?");
    
    // WhiteSpace (thanks to tchrist on stackoverflow)
    String whitespace =  ""
      + "\\u0009" // CHARACTER TABULATION
      + "\\u000A" // LINE FEED (LF)
      + "\\u000B" // LINE TABULATION
      + "\\u000C" // FORM FEED (FF)
      + "\\u000D" // CARRIAGE RETURN (CR)
      + "\\u0020" // SPACE
      + "\\u0085" // NEXT LINE (NEL) 
      + "\\u00A0" // NO-BREAK SPACE
      + "\\u1680" // OGHAM SPACE MARK
      + "\\u180E" // MONGOLIAN VOWEL SEPARATOR
      + "\\u2000" // EN QUAD 
      + "\\u2001" // EM QUAD 
      + "\\u2002" // EN SPACE
      + "\\u2003" // EM SPACE
      + "\\u2004" // THREE-PER-EM SPACE
      + "\\u2005" // FOUR-PER-EM SPACE
      + "\\u2006" // SIX-PER-EM SPACE
      + "\\u2007" // FIGURE SPACE
      + "\\u2008" // PUNCTUATION SPACE
      + "\\u2009" // THIN SPACE
      + "\\u200A" // HAIR SPACE
      + "\\u2028" // LINE SEPARATOR
      + "\\u2029" // PARAGRAPH SEPARATOR
      + "\\u202F" // NARROW NO-BREAK SPACE
      + "\\u205F" // MEDIUM MATHEMATICAL SPACE
      + "\\u3000" // IDEOGRAPHIC SPACE
      ;        
    s = s.replaceAll("["+whitespace+"]+", " "); // whitespace
    
    // Look for any funny characters (whitelist allowed chars)
    Matcher matcher = Pattern.compile("[^A-Za-z0-9:\\-',\\.!\\? \\(\\);/\\$\\&\\+\\=\\%]").matcher(s);
    if (matcher.find()) {
      String errStr = s.substring(matcher.start() + (matcher.start() > 10 ? -10 : 0));
      char funnyChar = s.charAt(matcher.start());
      throw new RuntimeException("\n\nFunny char '"+funnyChar+"' code="+String.format("\\u%04x",(int)funnyChar)+" in \n"+str+"\n"+errStr+"\n");
    }
    
    return s.trim();
  }
  
  /**
   * String shortening, removes :
   *  - periods
   *  - extra whitespace
   *  - non-quoteable text
   * @param str to shorten
   * @return the shortened String, null if str is null
   */
  public String shorten(String str) {
    if (str == null) return null;
    
    String s = str.replaceAll("\\.", "").trim();
    // Remove uneeded prefix words
    s = s.replaceFirst("^Thus[,]? ", "");
    s = s.replaceFirst("^Therefore[,]? ", "");
    s = s.replaceFirst("^Furthermore[,]? ", "");
    s = s.replaceFirst("^Likewise[,]? ", "");
    s = s.replaceFirst("^Moreover[,]? ", "");
    s = s.replaceFirst("^Yet[,]? ", "");
    s = s.replaceFirst("^However[,]? ", "");
    s = s.replaceFirst("^Rather[,]? ", "");
    s = s.replaceFirst("^Instead[,]? ", "");
    s = s.replaceFirst("^Nevertheless[,]? ", "");
    s = s.replaceFirst("^No, ", "").replaceFirst("^Yes[,]* ", "");
    s = s.replaceFirst("^But[,]? ", "");
    s = s.replaceFirst("^On the contrary[,]? ", "");
    s = s.replaceFirst("^On the other hand[,]? ", "");
    s = s.replaceFirst("^By contrast[,]? ", "");
    s = s.replaceFirst("^First[ly,]* ", "").replaceFirst("^Second[ly,]* ", "").replaceFirst("^Third[ly,]* ", "").replaceFirst("^Fourth[ly,]* ", "");
    s = s.replaceFirst("^Fifth[ly,]* ", "").replaceFirst("^Sixth[ly,]* ", "").replaceFirst("^Seven[thly,]* ", "").replaceFirst("^Eigh[thly,]* ", "");
    s = s.replaceFirst("^Finally[,]? ", "");
    s = s.replaceFirst("^So[,]? ", "");
    s = s.replaceFirst("^Then[,]? ", "");
    s = s.replaceFirst("^And[,]? ", "");
    s = s.replaceFirst("^Here[,]? ", "");
    s = s.replaceFirst("^Hence[,]? ", "");
    s = s.replaceFirst("^Also[,]? ", "");    
    s = s.replaceFirst("^Actually[,]? ", "");
    s = s.replaceFirst("^Eventually[,]? ", "");
    s = s.replaceFirst("^In conclusion[,]? ", "");
    s = s.replaceFirst("^In fact[,]? ", "");
    s = s.replaceFirst("^In like manner[,]? ", "");
    s = s.replaceFirst("^To this end[,]? ", "");
    s = s.replaceFirst("^This means that[,]? ", "");
    s = s.replaceFirst("^To repeat[,]? ", "");
    s = s.replaceFirst("^Once again[,]? ", "");
    s = s.replaceFirst("^Prayer[:]? ", "");
    
    // extra space around commas (probably from removed bits)
    s = s.replaceFirst(" , ", ", ");
    
    // InitCap (in case the above lines cut out a starting word)
    if (s.length() > 0) {
      s = Character.toUpperCase(s.charAt(0))+s.substring(1);
    }
  
    // Funny starting characters
    if (s.startsWith("'") || s.startsWith("/")) {
      s = s.substring(1);
    }
    return s.trim();
  }
  
  /**
   * Apply vigorous twitter-style shortening
   * @param str to shorten
   * @return the greatly abbreviated String
   */
  public String shortenMore(String str) {
    if (str == null) return null;
    String s = str;
    s = s.replaceFirst("^Oh[,]* ", "");
    s = s.replaceFirst("^Brothers and sisters[,]* ", "");
    s = s.replaceFirst("^Brother[s,]* ", "");
    s = s.replaceFirst("^Sister[s,]* ", "");
    // InitCap (in case the above lines removed the first word)
    if (s.length() > 0) {
      s = Character.toUpperCase(s.charAt(0))+s.substring(1);
    }
    
    // Twitter abbreviations
    //s = s.replaceAll(" and ", " & ").replaceAll("[Yy]ou", "u");
    //s = s.replaceAll("[B]efore", "b4").replaceAll("[Ff]or[e]* ", "4");
    
    // Trim all non alpha-numeric
    s = s.replaceAll("[^A-Za-z0-9 -&]", "");    
    s = s.replaceAll("\\s+", " ").trim(); // extra whitespace
    return s;
  }
  
  
  /**
   * Tries to find suitable quotes
   * @param str The sentence to filter
   * @return "" if unsuitable, the sentence, or a modified version of the sentence if suitable, null if str is null 
   */
  public String filter(String str) {
    String s = str;
    if (str == null) return null;
    
    // Check for personal stuff (I or me) 
    if (    ((s.startsWith("I ") || s.matches(".* I .*") || s.endsWith(" I"))) 
         || ((s.matches(".* me .*") || s.endsWith(" me"))) ) {
      return "";
    }

    // Sentences that need context are not good quotes  (his = "this" or "This")
    if (s.startsWith("This") || s.startsWith("For instance") || s.startsWith("For example") ||
        s.contains("his verse") || s.contains("his chapter") || s.contains("his book") ||
        s.startsWith("Question")) {
      return "";
    }
    
    // Most good quotes are longer sentences
    if (s.length() < 110) {
      return "";
    }
    
    // If it's long, see if we can shorten it a bit and make it work
    if (s.length() > 140) {
      s = shortenMore(s);
    }
    
    // It's too long, even after all the shortening we can do
    if (s.length() > 140) {
      return "";
    }
    
    return s;
  }
  
  
  /**
   * Finds suitable quotes 
   * @param paragraph to parse
   */
  public void findQuotes(String paragraph) {
    if (paragraph == null) return; 
    
    Scanner scanner = new Scanner(clean(paragraph));
    String sentence = null;
    do {
      sentence = shorten(scanner.findWithinHorizon(".*?[\\.!\\?]", 0));
      sentence = filter(sentence);
      if ((sentence != null) && (sentence.length() > 0)) {
        storeQuote(sentence);
      }
    } while (sentence != null);
    
  }
  
  
  /**
   * Opens the file, finds all the paragraphs and calls findQuotes on the contents
   * @param page File to process
   */
  public void processFile(File page) {
    try {
      System.out.println("------------------ "+page+" -----------------------");
      Document doc = Jsoup.parse(page, "UTF-8");
      Element bodyTag = doc.getElementsByTag("body").first();
      Elements elements = bodyTag.getAllElements();
      // Ignore the first element, it is the body tag itself
      for (int i=1; i<elements.size(); i++) {
        Element e = elements.get(i);
        String tagName = e.tagName().toLowerCase();
        String text = e.text();
        if (tagName.matches("(p)|(blockquote)")) {
          findQuotes(text);
        }
        // All the other tags 
        // "([hH][0-9])|(em)|(br)|(table)|(li)|(ol)|(tr)|(td)|(tbody)|(a)|(ul)|(strong)|(span)|(div)|(i)|(sup)|(center)|"+
        // "(font)|(sub)|(b)|(img)|(thead)|(th)|(ph2)|(u)"
      } // for
    } catch (IOException e) {
      e.printStackTrace();
    }
  }
  
  
  
  /**
   * Stores the quote
   * @param quote
   */
  public void storeQuote(String quote) {
    System.out.println("("+quote.length()+") "+quote);
    try {
      out.write(quote+"\n");
    } catch (Exception e) {
      e.printStackTrace();
    }
  }
  
  /**
   * Quietly close the file. Java should have this method.
   * @param c
   */
  public static void closeQuietly(Closeable c) {
    try { 
      if (c != null) c.close(); 
    } catch (Exception e) { }
  }
  
  /**
   * Go through all the books and files and process each page
   *  This will expect a particular structure of a list of directories, with files in them. 
   *  This will NOT handle arbitrary directory depth or structures.
   * Expected Structure : {path}/bookname/filename.html
   * @param path : root path 
   */
  public void findFiles(String path) {
    File root = new File(BOOK_PATH);
    File[] books = root.listFiles();
    
    if (books != null) {
      for (File book: books) {
        System.out.println("\n\n ====================== "+book+" ====================================\n");
        try {
          out = new BufferedWriter(new FileWriter(OUTPUT_PATH+File.separator+book.getName()+".txt"));
          
          File[] pages = book.listFiles();
          if (pages != null) {
            for (File page : pages) {
              if (page.isFile()) {
                processFile(page);
              }
            } // for page
          }
          
        } catch (IOException e) {
          e.printStackTrace();
        } finally {
          closeQuietly(out);             
        }
      } // for book
    }  
  }
  
  /**
   * Main Method - Processes all the books
   * @param args not used
   */
  public static void main(String[] args) {
    QuoteFinder quoteFinder = new QuoteFinder();
    quoteFinder.findFiles(BOOK_PATH);
    System.out.println("Done");
  }
}
